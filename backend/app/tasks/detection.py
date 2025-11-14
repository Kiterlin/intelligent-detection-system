"""
检测相关的 Celery 异步任务
"""
import asyncio
from pathlib import Path
from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from app.celery_app import celery_app
from app.core.config import settings
from app.models.detection_history import DetectionStatus
from app.crud.detection import (
    get_detection_by_id,
    update_detection_status,
    update_detection_result,
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


class DetectionTask(Task):
    """自定义Celery任务基类，用于检测任务"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"任务失败 {task_id}: {exc}")
        # 这里可以添加额外的失败处理逻辑


@celery_app.task(bind=True, base=DetectionTask, name="tasks.process_video_detection")
def process_video_detection(self, detection_id: int):
    """
    处理视频检测任务（Celery任务）

    Args:
        detection_id: 检测记录ID
    """
    # 使用 asyncio 运行异步任务
    return asyncio.run(_async_process_video_detection(self, detection_id))


async def _async_process_video_detection(task: Task, detection_id: int):
    """
    异步处理视频检测

    Args:
        task: Celery任务实例
        detection_id: 检测记录ID

    Returns:
        dict: 检测结果
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"开始处理视频检测任务 ID={detection_id}")

            # 获取检测记录
            detection_record = await get_detection_by_id(db, detection_id)
            if not detection_record:
                raise ValueError(f"检测记录不存在: {detection_id}")

            # 更新状态为处理中
            await update_detection_status(
                db, detection_id, DetectionStatus.PROCESSING
            )

            # 获取模型信息
            model_record = await get_model_by_id(db, detection_record.model_id)
            if not model_record:
                raise ValueError(f"模型不存在: {detection_record.model_id}")

            # 加载模型
            model = model_loader.load_model(model_record.id, model_record.file_path)

            # 创建检测服务
            detection_service = DetectionService(model)

            # 准备输出路径
            output_dir = (
                Path(settings.DETECTION_OUTPUT_DIR) / str(detection_record.user_id)
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            input_filename = Path(detection_record.input_file_path).stem
            output_filename = f"output_{input_filename}.mp4"
            output_path = output_dir / output_filename

            # 定义进度回调函数
            def progress_callback(current_frame: int, total_frames: int):
                progress = (current_frame / total_frames) * 100
                # 更新任务进度
                task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": current_frame,
                        "total": total_frames,
                        "progress": progress,
                    },
                )
                logger.info(
                    f"视频检测进度 ID={detection_id}: {current_frame}/{total_frames} ({progress:.1f}%)"
                )

            # 执行视频检测
            detections, processing_time = detection_service.detect_video(
                video_path=detection_record.input_file_path,
                output_path=str(output_path),
                confidence_threshold=detection_record.confidence_threshold,
                iou_threshold=detection_record.iou_threshold,
                progress_callback=progress_callback,
            )

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

            logger.info(
                f"视频检测任务完成 ID={detection_id}, 对象数={len(detections)}, 耗时={processing_time:.2f}s"
            )

            # 检查并触发告警（不影响检测任务）
            try:
                alert_stats = await check_and_trigger_alerts(
                    db=db,
                    detection_id=detection_id,
                    user_id=detection_record.user_id,
                    result_json=result_json,
                )
                logger.info(f"Alert check stats for detection {detection_id}: {alert_stats}")
            except Exception as alert_error:
                logger.error(f"Alert check failed for detection {detection_id}: {alert_error}")

            return {
                "detection_id": detection_id,
                "detected_count": len(detections),
                "processing_time": processing_time,
                "output_path": str(output_path),
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"视频检测任务失败 ID={detection_id}: {str(e)}")

            # 更新检测状态为失败
            try:
                await update_detection_status(
                    db, detection_id, DetectionStatus.FAILED, error_message=str(e)
                )
            except Exception as update_error:
                logger.error(f"更新检测状态失败: {str(update_error)}")

            # 重新抛出异常以便Celery记录
            raise
