"""
检测相关 API 端点
"""
import os
import time
from datetime import datetime
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.detection_history import DetectionInputType, DetectionStatus
from app.crud.ml_model import get_active_model
from app.crud.detection import (
    create_detection,
    update_detection_result,
    update_detection_status,
    get_detection_by_id,
    get_detection_by_task_id,
    get_detections_with_filter,
    delete_detection,
    get_user_detection_stats,
)
from app.schemas.detection import (
    ImageDetectionResponse,
    DetectionObject,
    VideoDetectionResponse,
    TaskStatusResponse,
    DetectionHistoryResponse,
    DetectionHistoryListResponse,
    DetectionStatsResponse,
)
from app.services.model_loader import model_loader
from app.services.detection import DetectionService
from app.tasks.detection import process_video_detection
from app.celery_app import celery_app
from loguru import logger

router = APIRouter()


def _validate_image_file(file: UploadFile) -> None:
    """
    验证上传的图像文件

    Args:
        file: 上传的文件

    Raises:
        HTTPException: 文件验证失败
    """
    # 验证文件格式
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图像格式: {file_ext}，支持格式: {', '.join(settings.SUPPORTED_IMAGE_FORMATS)}",
        )

    # 验证文件大小
    if file.size and file.size > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"图像文件过大，最大支持 {settings.MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB",
        )


def _validate_video_file(file: UploadFile) -> None:
    """
    验证上传的视频文件

    Args:
        file: 上传的文件

    Raises:
        HTTPException: 文件验证失败
    """
    # 验证文件格式
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.SUPPORTED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的视频格式: {file_ext}，支持格式: {', '.join(settings.SUPPORTED_VIDEO_FORMATS)}",
        )

    # 验证文件大小
    if file.size and file.size > settings.MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"视频文件过大，最大支持 {settings.MAX_VIDEO_SIZE / 1024 / 1024:.1f}MB",
        )


async def _save_uploaded_file(file: UploadFile, user_id: int, prefix: str) -> str:
    """
    保存上传的文件

    Args:
        file: 上传的文件
        user_id: 用户ID
        prefix: 文件名前缀

    Returns:
        保存的文件路径
    """
    # 创建用户目录
    user_dir = Path(settings.DETECTION_INPUT_DIR) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(file.filename).suffix
    filename = f"{prefix}_{timestamp}{file_ext}"
    file_path = user_dir / filename

    # 保存文件
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path)


@router.post("/image", response_model=ImageDetectionResponse)
async def detect_image(
    file: UploadFile = File(..., description="要检测的图像文件"),
    confidence_threshold: float = Form(
        settings.DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="置信度阈值",
    ),
    iou_threshold: float = Form(
        settings.DEFAULT_IOU_THRESHOLD, ge=0.0, le=1.0, description="IOU阈值"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    图像目标检测

    上传图像进行同步检测，返回检测结果和标注后的图像
    """
    # 验证文件
    _validate_image_file(file)

    # 获取激活的模型
    active_model = await get_active_model(db)
    if not active_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="当前没有激活的检测模型，请联系管理员",
        )

    try:
        # 保存上传的图像
        input_path = await _save_uploaded_file(file, current_user.id, "input")
        logger.info(f"用户 {current_user.id} 上传图像: {input_path}")

        # 创建检测记录
        detection_record = await create_detection(
            db=db,
            user_id=current_user.id,
            model_id=active_model.id,
            input_type=DetectionInputType.IMAGE,
            input_file_path=input_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )

        # 加载模型
        model = model_loader.load_model(active_model.id, active_model.file_path)

        # 创建检测服务
        detection_service = DetectionService(model)

        # 执行检测
        start_time = time.time()
        detections, annotated_image = detection_service.detect_image(
            image_path=input_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )
        processing_time = time.time() - start_time

        # 保存标注后的图像
        output_dir = Path(settings.DETECTION_OUTPUT_DIR) / str(current_user.id)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}{Path(file.filename).suffix}"
        output_path = output_dir / output_filename

        detection_service.save_annotated_image(annotated_image, str(output_path))

        # 转换结果为JSON
        result_json = detection_service.results_to_json(detections)

        # 更新检测记录
        await update_detection_result(
            db=db,
            detection_id=detection_record.id,
            output_file_path=str(output_path),
            result_json=result_json,
            detected_objects_count=len(detections),
            processing_time=processing_time,
        )

        logger.info(
            f"图像检测完成 ID={detection_record.id}, 对象数={len(detections)}, 耗时={processing_time:.2f}s"
        )

        # 构建响应
        detection_objects = [DetectionObject(**det) for det in detections]

        return ImageDetectionResponse(
            detection_id=detection_record.id,
            objects=detection_objects,
            detected_count=len(detections),
            processing_time=processing_time,
            output_file_path=str(output_path),
        )

    except FileNotFoundError as e:
        logger.error(f"文件未找到: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文件未找到"
        )
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"图像检测失败: {str(e)}")

        # 更新检测状态为失败
        if "detection_record" in locals():
            await update_detection_status(
                db=db,
                detection_id=detection_record.id,
                status=DetectionStatus.FAILED,
                error_message=str(e),
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测失败: {str(e)}",
        )


@router.post("/video", response_model=VideoDetectionResponse)
async def detect_video(
    file: UploadFile = File(..., description="要检测的视频文件"),
    confidence_threshold: float = Form(
        settings.DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="置信度阈值",
    ),
    iou_threshold: float = Form(
        settings.DEFAULT_IOU_THRESHOLD, ge=0.0, le=1.0, description="IOU阈值"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    视频目标检测

    上传视频进行异步检测，返回任务ID用于查询进度
    """
    # 验证文件
    _validate_video_file(file)

    # 获取激活的模型
    active_model = await get_active_model(db)
    if not active_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="当前没有激活的检测模型，请联系管理员",
        )

    try:
        # 保存上传的视频
        input_path = await _save_uploaded_file(file, current_user.id, "input")
        logger.info(f"用户 {current_user.id} 上传视频: {input_path}")

        # 创建检测记录（稍后由任务更新task_id）
        detection_record = await create_detection(
            db=db,
            user_id=current_user.id,
            model_id=active_model.id,
            input_type=DetectionInputType.VIDEO,
            input_file_path=input_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )

        # 提交Celery任务
        task = process_video_detection.delay(detection_record.id)

        # 更新检测记录的task_id
        detection_record.task_id = task.id
        await db.commit()

        logger.info(f"视频检测任务已提交 ID={detection_record.id}, task_id={task.id}")

        return VideoDetectionResponse(
            task_id=task.id,
            detection_id=detection_record.id,
            message="视频检测任务已提交，请使用task_id查询进度",
        )

    except Exception as e:
        logger.error(f"提交视频检测任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交任务失败: {str(e)}",
        )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    查询检测任务状态

    根据task_id查询视频检测任务的进度和结果
    """
    try:
        # 获取任务结果
        task_result = celery_app.AsyncResult(task_id)

        # 从数据库获取检测记录
        detection_record = await get_detection_by_task_id(db, task_id)
        if not detection_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="检测记录不存在",
            )

        # 验证用户权限
        if detection_record.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此检测记录",
            )

        # 构建响应
        response = TaskStatusResponse(
            task_id=task_id,
            status=detection_record.status,
            detection_id=detection_record.id,
        )

        # 根据任务状态添加额外信息
        if task_result.state == "PROGRESS":
            # 任务进行中，返回进度
            progress_info = task_result.info
            response.progress = progress_info.get("progress", 0)
            response.message = f"处理中: {progress_info.get('current', 0)}/{progress_info.get('total', 0)} 帧"

        elif detection_record.status == DetectionStatus.COMPLETED:
            # 任务完成，返回结果
            response.message = "检测完成"
            response.result = {
                "detected_count": detection_record.detected_objects_count,
                "processing_time": detection_record.processing_time,
                "output_path": detection_record.output_file_path,
            }

        elif detection_record.status == DetectionStatus.FAILED:
            # 任务失败
            response.message = f"检测失败: {detection_record.error_message}"

        elif detection_record.status == DetectionStatus.PROCESSING:
            response.message = "任务正在处理中..."

        else:
            response.message = "任务等待处理"

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询任务状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}",
        )


@router.get("/history", response_model=DetectionHistoryListResponse)
async def get_detection_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    input_type: Optional[DetectionInputType] = Query(None, description="输入类型筛选"),
    status: Optional[DetectionStatus] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取检测历史列表

    支持分页、类型筛选和状态筛选
    """
    try:
        skip = (page - 1) * page_size

        histories, total = await get_detections_with_filter(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=page_size,
            input_type=input_type,
            status=status,
        )

        return DetectionHistoryListResponse(
            histories=histories,
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error(f"获取检测历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史失败: {str(e)}",
        )


@router.get("/history/{detection_id}", response_model=DetectionHistoryResponse)
async def get_detection_detail(
    detection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取检测历史详情

    根据ID获取单条检测记录的详细信息
    """
    detection = await get_detection_by_id(db, detection_id)

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测记录不存在",
        )

    # 验证用户权限
    if detection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此检测记录",
        )

    return detection


@router.delete("/history/{detection_id}")
async def delete_detection_record(
    detection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除检测历史记录

    删除指定的检测记录（包括关联的文件）
    """
    detection = await get_detection_by_id(db, detection_id)

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测记录不存在",
        )

    # 验证用户权限
    if detection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此检测记录",
        )

    try:
        # 删除相关文件
        if detection.input_file_path and os.path.exists(detection.input_file_path):
            os.remove(detection.input_file_path)

        if detection.output_file_path and os.path.exists(detection.output_file_path):
            os.remove(detection.output_file_path)

        # 删除数据库记录
        success = await delete_detection(db, detection_id)

        if success:
            logger.info(f"检测记录已删除 ID={detection_id}")
            return {"message": "删除成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除失败",
            )

    except Exception as e:
        logger.error(f"删除检测记录失败 ID={detection_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}",
        )


@router.get("/download/{detection_id}")
async def download_result(
    detection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    下载检测结果文件

    下载指定检测记录的输出文件（标注后的图像或视频）
    """
    detection = await get_detection_by_id(db, detection_id)

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测记录不存在",
        )

    # 验证用户权限
    if detection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此检测记录",
        )

    # 检查输出文件是否存在
    if not detection.output_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="输出文件不存在（检测可能未完成）",
        )

    if not os.path.exists(detection.output_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="输出文件已被删除",
        )

    # 返回文件
    filename = Path(detection.output_file_path).name
    return FileResponse(
        path=detection.output_file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.get("/stats", response_model=DetectionStatsResponse)
async def get_detection_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取检测统计信息

    获取当前用户的检测统计数据
    """
    try:
        stats = await get_user_detection_stats(db, current_user.id)
        return DetectionStatsResponse(**stats)

    except Exception as e:
        logger.error(f"获取检测统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}",
        )
