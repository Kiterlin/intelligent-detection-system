"""
数据集相关 API 端点
"""
import os
import aiofiles
from datetime import datetime
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.dataset import BatchJobStatus
from app.crud.dataset import (
    create_dataset,
    get_dataset_by_id,
    get_user_datasets,
    get_dataset_with_files,
    update_dataset,
    delete_dataset,
    add_file_to_dataset,
    get_dataset_files,
    create_batch_job,
    get_batch_job_by_id,
    get_user_batch_jobs,
    get_dataset_batch_jobs,
)
from app.crud.ml_model import get_model_by_id
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    DatasetDetailResponse,
    DatasetListResponse,
    DataFileResponse,
    BatchJobCreate,
    BatchJobResponse,
    BatchJobDetailResponse,
    BatchJobListResponse,
    FileUploadResponse,
    BatchUploadResponse,
)
from app.tasks.batch_detection import start_batch_detection
from loguru import logger

router = APIRouter()


# ==================== 辅助函数 ====================

def _validate_dataset_file(file: UploadFile) -> None:
    """
    验证上传的数据集文件

    Args:
        file: 上传的文件

    Raises:
        HTTPException: 文件验证失败
    """
    # 验证文件格式
    file_ext = Path(file.filename).suffix.lower()
    supported_formats = settings.SUPPORTED_IMAGE_FORMATS + settings.SUPPORTED_VIDEO_FORMATS
    if file_ext not in supported_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式: {file_ext}，支持格式: {', '.join(supported_formats)}",
        )

    # 验证文件大小
    max_size = max(settings.MAX_IMAGE_SIZE, settings.MAX_VIDEO_SIZE)
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大，最大支持 {max_size / 1024 / 1024:.1f}MB",
        )


async def _save_dataset_file(
    file: UploadFile, dataset_id: int, user_id: int
) -> tuple[str, int, str]:
    """
    保存数据集文件

    Args:
        file: 上传的文件
        dataset_id: 数据集ID
        user_id: 用户ID

    Returns:
        (文件路径, 文件大小, 文件类型) 元组
    """
    # 创建数据集目录
    dataset_dir = Path(settings.DATASET_DIR) / str(user_id) / str(dataset_id)
    dataset_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(file.filename).suffix
    safe_filename = Path(file.filename).stem[:50]  # 限制文件名长度
    filename = f"{safe_filename}_{timestamp}{file_ext}"
    file_path = dataset_dir / filename

    # 异步保存文件
    content = await file.read()
    file_size = len(content)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 判断文件类型
    if file_ext in settings.SUPPORTED_IMAGE_FORMATS:
        file_type = "image"
    elif file_ext in settings.SUPPORTED_VIDEO_FORMATS:
        file_type = "video"
    else:
        file_type = "unknown"

    return str(file_path), file_size, file_type


def _build_dataset_response(dataset, files: List = None) -> DatasetResponse:
    """构建数据集响应对象"""
    if files is None:
        files_list = list(getattr(dataset, "files", []) or [])
    else:
        files_list = files

    # 计算统计信息
    file_count = len(files_list)
    total_size = sum((f.file_size or 0) for f in files_list)

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        user_id=dataset.user_id,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        file_count=file_count,
        total_size=total_size,
    )


def _build_batch_job_detail_response(job: BatchJobResponse) -> BatchJobDetailResponse:
    """构建批量任务详情响应对象"""
    return BatchJobDetailResponse(
        id=job.id,
        dataset_id=job.dataset_id,
        user_id=job.user_id,
        model_id=job.model_id,
        status=job.status,
        total_files=job.total_files,
        completed_files=job.completed_files,
        failed_files=job.failed_files,
        confidence_threshold=job.confidence_threshold,
        iou_threshold=job.iou_threshold,
        celery_group_id=job.celery_group_id,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        progress=job.progress_percentage,
        dataset_name=job.dataset.name if job.dataset else None,
        model_name=job.model.name if job.model else None,
    )


# ==================== 数据集 CRUD API ====================

@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_new_dataset(
    dataset_in: DatasetCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新数据集

    - **name**: 数据集名称（必填）
    - **description**: 数据集描述（可选）
    """
    logger.info(f"User {current_user.id} creating dataset: {dataset_in.name}")

    try:
        dataset = await create_dataset(
            db=db,
            name=dataset_in.name,
            user_id=current_user.id,
            description=dataset_in.description,
        )

        return _build_dataset_response(dataset, [])

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户数据集列表

    - 支持分页
    - 支持按名称和描述搜索
    """
    logger.info(f"User {current_user.id} listing datasets (skip={skip}, limit={limit}, search={search})")

    datasets, total = await get_user_datasets(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
    )

    items = [_build_dataset_response(ds) for ds in datasets]

    return DatasetListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
async def get_dataset_detail(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取数据集详情（包含文件列表）
    """
    logger.info(f"User {current_user.id} getting dataset {dataset_id}")

    dataset = await get_dataset_with_files(
        db=db,
        dataset_id=dataset_id,
        user_id=current_user.id,
    )

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在或无权限访问",
        )

    # 构建响应
    files = [DataFileResponse.from_orm(f) for f in dataset.files]
    response = _build_dataset_response(dataset, dataset.files)

    return DatasetDetailResponse(
        **response.dict(),
        files=files,
    )


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset_info(
    dataset_id: int,
    dataset_update: DatasetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新数据集信息
    """
    logger.info(f"User {current_user.id} updating dataset {dataset_id}")

    dataset = await update_dataset(
        db=db,
        dataset_id=dataset_id,
        user_id=current_user.id,
        name=dataset_update.name,
        description=dataset_update.description,
    )

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在或无权限访问",
        )

    # 重新加载文件列表以计算统计
    dataset = await get_dataset_with_files(db, dataset_id, current_user.id)
    return _build_dataset_response(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset_by_id(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除数据集（级联删除文件和任务）
    """
    logger.info(f"User {current_user.id} deleting dataset {dataset_id}")

    success = await delete_dataset(
        db=db,
        dataset_id=dataset_id,
        user_id=current_user.id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在或无权限访问",
        )

    # TODO: 删除物理文件
    # dataset_dir = Path(settings.DATASET_DIR) / str(current_user.id) / str(dataset_id)
    # if dataset_dir.exists():
    #     shutil.rmtree(dataset_dir)

    return None


# ==================== 文件管理 API ====================

@router.post("/{dataset_id}/files", response_model=BatchUploadResponse)
async def upload_files_to_dataset(
    dataset_id: int,
    files: List[UploadFile] = File(..., description="要上传的文件列表"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传文件到数据集（支持批量上传）

    - 支持图片和视频
    - 自动识别文件类型
    """
    logger.info(f"User {current_user.id} uploading {len(files)} files to dataset {dataset_id}")

    # 验证数据集所有权
    dataset = await get_dataset_by_id(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在或无权限访问",
        )

    # 验证文件数量
    if len(files) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次最多上传50个文件",
        )

    uploaded_files = []
    total_size = 0

    for file in files:
        try:
            # 验证文件
            _validate_dataset_file(file)

            # 保存文件
            file_path, file_size, file_type = await _save_dataset_file(
                file, dataset_id, current_user.id
            )

            # 添加到数据库
            db_file = await add_file_to_dataset(
                db=db,
                dataset_id=dataset_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
            )

            uploaded_files.append(
                FileUploadResponse(
                    file_id=db_file.id,
                    filename=db_file.filename,
                    file_size=db_file.file_size,
                    file_type=db_file.file_type,
                )
            )
            total_size += file_size

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"上传文件 {file.filename} 失败: {str(e)}",
            )

    return BatchUploadResponse(
        dataset_id=dataset_id,
        uploaded_files=uploaded_files,
        total_uploaded=len(uploaded_files),
        total_size=total_size,
    )


@router.get("/{dataset_id}/files", response_model=List[DataFileResponse])
async def list_dataset_files(
    dataset_id: int,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大记录数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取数据集文件列表
    """
    # 验证数据集所有权
    dataset = await get_dataset_by_id(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在或无权限访问",
        )

    files, total = await get_dataset_files(
        db=db,
        dataset_id=dataset_id,
        skip=skip,
        limit=limit,
    )

    return [DataFileResponse.from_orm(f) for f in files]


# ==================== 批量检测 API ====================

@router.post("/{dataset_id}/batch-detect", response_model=BatchJobResponse)
async def start_batch_detection_job(
    dataset_id: int,
    job_in: BatchJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    启动批量检测任务

    - 对数据集中的所有文件执行检测
    - 使用 Celery Chain 顺序处理
    - 返回任务ID用于查询进度
    """
    logger.info(f"User {current_user.id} starting batch detection for dataset {dataset_id}")

    # 验证数据集所有权
    dataset = await get_dataset_with_files(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在或无权限访问",
        )

    # 检查数据集是否有文件
    if not dataset.files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据集中没有文件",
        )

    # 验证模型
    model = await get_model_by_id(db, job_in.model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在",
        )

    # 创建批量任务
    batch_job = await create_batch_job(
        db=db,
        dataset_id=dataset_id,
        user_id=current_user.id,
        model_id=job_in.model_id,
        total_files=len(dataset.files),
        confidence_threshold=job_in.confidence_threshold,
        iou_threshold=job_in.iou_threshold,
    )

    # 启动 Celery 批量任务
    try:
        celery_task = start_batch_detection.delay(
            dataset_id=dataset_id,
            model_id=job_in.model_id,
            job_id=batch_job.id,
            user_id=current_user.id,
            confidence_threshold=job_in.confidence_threshold,
            iou_threshold=job_in.iou_threshold,
        )

        logger.info(f"Batch job {batch_job.id} started with Celery task {celery_task.id}")

    except Exception as e:
        logger.error(f"Error starting batch detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动批量任务失败: {str(e)}",
        )

    return BatchJobResponse.from_orm(batch_job)


@router.get("/batch-jobs/{job_id}", response_model=BatchJobDetailResponse)
async def get_batch_job_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    查询批量任务状态和进度
    """
    job = await get_batch_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批量任务不存在或无权限访问",
        )

    return _build_batch_job_detail_response(job)


@router.get("/batch-jobs", response_model=BatchJobListResponse)
async def list_batch_jobs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    status: Optional[BatchJobStatus] = Query(None, description="状态过滤"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户批量任务列表

    - 支持分页
    - 支持按状态过滤
    """
    logger.info(f"User {current_user.id} listing batch jobs (skip={skip}, limit={limit}, status={status})")

    jobs, total = await get_user_batch_jobs(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )

    items = [_build_batch_job_detail_response(job) for job in jobs]

    return BatchJobListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
