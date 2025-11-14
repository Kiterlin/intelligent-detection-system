"""
批量检测相关的 Celery 异步任务
"""
import asyncio
import json
from pathlib import Path
from celery import Task, chain
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from app.celery_app import celery_app
from app.core.config import settings
from app.models.detection_history import DetectionInputType, DetectionStatus
from app.models.dataset import BatchJobStatus
from app.crud.detection import create_detection, update_detection_result, update_detection_status
from app.crud.dataset import (
    get_batch_job_by_id,
    update_batch_job_status,
    update_batch_job_progress,
    get_file_by_id,
)
from app.crud.ml_model import get_model_by_id
from app.services.model_loader import model_loader
from app.services.detection import DetectionService
from app.services.alert_integration import check_and_trigger_alerts


# 创建异步数据库引擎（用于任务中）
async_engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


class BatchDetectionTask(Task):
    """自定义Celery任务基类，用于批量检测任务"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"批量检测任务失败 {task_id}: {exc}")


@celery_app.task(bind=True, base=BatchDetectionTask, name="tasks.process_single_file_in_batch")
def process_single_file_in_batch(
    self,
    file_id: int,
    model_id: int,
    job_id: int,
    user_id: int,
    confidence_threshold: float,
    iou_threshold: float,
):
    """
    处理批量任务中的单个文件

    Args:
        file_id: 文件ID
        model_id: 模型ID
        job_id: 批量任务ID
        user_id: 用户ID
        confidence_threshold: 置信度阈值
        iou_threshold: IOU阈值

    Returns:
        dict: 处理结果
    """
    return asyncio.run(
        _async_process_single_file(
            self, file_id, model_id, job_id, user_id, confidence_threshold, iou_threshold
        )
    )


async def _async_process_single_file(
    task: Task,
    file_id: int,
    model_id: int,
    job_id: int,
    user_id: int,
    confidence_threshold: float,
    iou_threshold: float,
):
    """
    异步处理单个文件的检测

    Args:
        task: Celery任务实例
        file_id: 文件ID
        model_id: 模型ID
        job_id: 批量任务ID
        user_id: 用户ID
        confidence_threshold: 置信度阈值
        iou_threshold: IOU阈值

    Returns:
        dict: 处理结果
    """
    async with AsyncSessionLocal() as db:
        detection_id = None
        try:
            logger.info(f"开始处理文件 ID={file_id}, Job={job_id}")

            # 获取文件信息
            file_obj = await get_file_by_id(db, file_id)
            if not file_obj:
                raise ValueError(f"文件不存在: {file_id}")

            # 确定输入类型
            if file_obj.file_type == "image":
                input_type = DetectionInputType.IMAGE
            elif file_obj.file_type == "video":
                input_type = DetectionInputType.VIDEO
            else:
                raise ValueError(f"不支持的文件类型: {file_obj.file_type}")

            # 创建检测记录
            detection_record = await create_detection(
                db=db,
                user_id=user_id,
                model_id=model_id,
                input_type=input_type,
                input_file_path=file_obj.file_path,
                confidence_threshold=confidence_threshold,
                iou_threshold=iou_threshold,
                task_id=task.request.id,
            )
            detection_id = detection_record.id

            # 更新状态为处理中
            await update_detection_status(db, detection_id, DetectionStatus.PROCESSING)

            # 获取模型信息
            model_record = await get_model_by_id(db, model_id)
            if not model_record:
                raise ValueError(f"模型不存在: {model_id}")

            # 加载模型
            model = model_loader.load_model(model_record.id, model_record.file_path)

            # 创建检测服务
            detection_service = DetectionService(model)

            # 准备输出路径
            output_dir = Path(settings.DETECTION_OUTPUT_DIR) / str(user_id)
            output_dir.mkdir(parents=True, exist_ok=True)

            input_filename = Path(file_obj.file_path).stem
            file_ext = Path(file_obj.file_path).suffix

            # 根据文件类型执行检测
            if input_type == DetectionInputType.IMAGE:
                # 图像检测
                output_filename = f"output_{input_filename}.jpg"
                output_path = output_dir / output_filename

                detections, processing_time = detection_service.detect_image(
                    image_path=file_obj.file_path,
                    output_path=str(output_path),
                    confidence_threshold=confidence_threshold,
                    iou_threshold=iou_threshold,
                )

            elif input_type == DetectionInputType.VIDEO:
                # 视频检测
                output_filename = f"output_{input_filename}.mp4"
                output_path = output_dir / output_filename

                def progress_callback(current_frame: int, total_frames: int):
                    progress = (current_frame / total_frames) * 100
                    task.update_state(
                        state="PROGRESS",
                        meta={
                            "file_id": file_id,
                            "current": current_frame,
                            "total": total_frames,
                            "progress": progress,
                        },
                    )

                detections, processing_time = detection_service.detect_video(
                    video_path=file_obj.file_path,
                    output_path=str(output_path),
                    confidence_threshold=confidence_threshold,
                    iou_threshold=iou_threshold,
                    progress_callback=progress_callback,
                )

            else:
                raise ValueError(f"不支持的输入类型: {input_type}")

            # 转换结果为JSON
            result_json = detection_service.results_to_json(detections)

            # 更新检测结果
            await update_detection_result(
                db=db,
                detection_id=detection_id,
                output_file_path=str(output_path),
                result_json=result_json,
                detected_objects_count=len(detections),
                processing_time=processing_time,
            )

            # 检查并触发告警（不影响批量检测任务）
            try:
                alert_stats = await check_and_trigger_alerts(
                    db=db,
                    detection_id=detection_id,
                    user_id=user_id,
                    result_json=result_json,
                    dataset_id=file_obj.dataset_id,
                )
                logger.info(f"Alert check stats for batch detection {detection_id}: {alert_stats}")
            except Exception as alert_error:
                logger.error(f"Alert check failed for batch detection {detection_id}: {alert_error}")

            # 更新批量任务进度（成功完成一个文件）
            await update_batch_job_progress(db, job_id, completed_files=1)

            logger.info(
                f"文件检测完成 ID={file_id}, Job={job_id}, 对象数={len(detections)}, 耗时={processing_time:.2f}s"
            )

            return {
                "file_id": file_id,
                "detection_id": detection_id,
                "detected_count": len(detections),
                "processing_time": processing_time,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"文件检测失败 ID={file_id}, Job={job_id}: {str(e)}")

            # 如果有检测记录，更新为失败状态
            if detection_id:
                await update_detection_status(
                    db, detection_id, DetectionStatus.FAILED, error_message=str(e)
                )

            # 更新批量任务进度（失败一个文件）
            await update_batch_job_progress(db, job_id, failed_files=1)

            # 重新抛出异常以让Celery知道任务失败
            raise


@celery_app.task(bind=True, base=BatchDetectionTask, name="tasks.start_batch_detection")
def start_batch_detection(
    self,
    dataset_id: int,
    model_id: int,
    job_id: int,
    user_id: int,
    confidence_threshold: float,
    iou_threshold: float,
):
    """
    启动批量检测任务（使用 Chain 顺序处理文件）

    Args:
        dataset_id: 数据集ID
        model_id: 模型ID
        job_id: 批量任务ID
        user_id: 用户ID
        confidence_threshold: 置信度阈值
        iou_threshold: IOU阈值

    Returns:
        dict: 启动结果
    """
    return asyncio.run(
        _async_start_batch_detection(
            self, dataset_id, model_id, job_id, user_id, confidence_threshold, iou_threshold
        )
    )


async def _async_start_batch_detection(
    task: Task,
    dataset_id: int,
    model_id: int,
    job_id: int,
    user_id: int,
    confidence_threshold: float,
    iou_threshold: float,
):
    """
    异步启动批量检测任务

    Args:
        task: Celery任务实例
        dataset_id: 数据集ID
        model_id: 模型ID
        job_id: 批量任务ID
        user_id: 用户ID
        confidence_threshold: 置信度阈值
        iou_threshold: IOU阈值

    Returns:
        dict: 启动结果
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"启动批量检测任务 Job={job_id}, Dataset={dataset_id}")

            # 获取批量任务
            batch_job = await get_batch_job_by_id(db, job_id)
            if not batch_job:
                raise ValueError(f"批量任务不存在: {job_id}")

            # 获取数据集所有文件
            from app.crud.dataset import get_dataset_files
            files, total = await get_dataset_files(db, dataset_id, skip=0, limit=1000)

            if not files:
                raise ValueError(f"数据集中没有文件: {dataset_id}")

            logger.info(f"数据集 {dataset_id} 包含 {len(files)} 个文件")

            # 更新任务状态为 RUNNING
            await update_batch_job_status(db, job_id, BatchJobStatus.RUNNING)

            # 创建 Celery Chain - 顺序处理每个文件
            # Chain: task1 | task2 | task3 | ...
            tasks_chain = chain(
                *[
                    process_single_file_in_batch.s(
                        file_id=file_obj.id,
                        model_id=model_id,
                        job_id=job_id,
                        user_id=user_id,
                        confidence_threshold=confidence_threshold,
                        iou_threshold=iou_threshold,
                    )
                    for file_obj in files
                ]
            )

            # 启动 Chain
            result = tasks_chain.apply_async()

            logger.info(
                f"批量检测任务已启动 Job={job_id}, Chain ID={result.id}, 文件数={len(files)}"
            )

            return {
                "job_id": job_id,
                "dataset_id": dataset_id,
                "total_files": len(files),
                "chain_id": result.id,
                "status": "started",
            }

        except Exception as e:
            logger.error(f"启动批量检测任务失败 Job={job_id}: {str(e)}")

            # 更新任务状态为失败
            await update_batch_job_status(
                db, job_id, BatchJobStatus.FAILED, error_message=str(e)
            )

            raise
