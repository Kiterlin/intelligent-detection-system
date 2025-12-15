"""
训练任务模块
用于模型训练相关的异步任务
所有任务都会路由到 training 队列，由 GPU Worker (solo pool) 处理
"""
import time
import logging
import torch
from celery import Task
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.training_tasks.test_gpu_task")
def test_gpu_task(self: Task) -> dict:
    """
    GPU 环境测试任务
    用于验证 GPU Worker 配置和队列隔离

    Returns:
        dict: 包含 GPU 信息的字典
    """
    try:
        logger.info("=" * 60)
        logger.info("GPU 测试任务开始")
        logger.info("=" * 60)

        # 获取任务信息
        logger.info(f"Task ID: {self.request.id}")
        logger.info(f"Task Name: {self.name}")
        logger.info(f"Queue: {self.request.delivery_info.get('routing_key', 'unknown')}")

        # 检查 PyTorch CUDA
        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA Available: {cuda_available}")

        result = {
            "task_id": self.request.id,
            "task_name": self.name,
            "queue": self.request.delivery_info.get('routing_key', 'unknown'),
            "cuda_available": cuda_available,
            "pytorch_version": torch.__version__,
        }

        if cuda_available:
            device_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            device_name = torch.cuda.get_device_name(current_device)
            memory_allocated = torch.cuda.memory_allocated(current_device) / 1024**2  # MB
            memory_reserved = torch.cuda.memory_reserved(current_device) / 1024**2  # MB

            result.update({
                "device_count": device_count,
                "current_device": current_device,
                "device_name": device_name,
                "cuda_version": torch.version.cuda,
                "memory_allocated_mb": round(memory_allocated, 2),
                "memory_reserved_mb": round(memory_reserved, 2),
            })

            logger.info(f"GPU Count: {device_count}")
            logger.info(f"Current Device: {current_device}")
            logger.info(f"Device Name: {device_name}")
            logger.info(f"CUDA Version: {torch.version.cuda}")
            logger.info(f"Memory Allocated: {memory_allocated:.2f} MB")
            logger.info(f"Memory Reserved: {memory_reserved:.2f} MB")

            # 简单的 GPU 测试
            logger.info("执行简单的 GPU 计算测试...")
            x = torch.randn(1000, 1000, device='cuda')
            y = torch.randn(1000, 1000, device='cuda')

            start_time = time.time()
            z = torch.matmul(x, y)
            torch.cuda.synchronize()
            elapsed = time.time() - start_time

            result["gpu_compute_test_seconds"] = round(elapsed, 4)
            logger.info(f"GPU 计算测试完成 (耗时: {elapsed:.4f}s)")

            # 清理 GPU 内存
            del x, y, z
            torch.cuda.empty_cache()
            logger.info("GPU 内存已清理")

        else:
            logger.warning("GPU 不可用，使用 CPU")

        # 模拟耗时任务
        logger.info("模拟耗时任务（5秒）...")
        for i in range(5):
            time.sleep(1)
            logger.info(f"Progress: {(i+1)*20}%")
            self.update_state(
                state='PROGRESS',
                meta={'progress': (i+1)*20, 'status': f'测试进行中 {(i+1)*20}%'}
            )

        logger.info("=" * 60)
        logger.info("GPU 测试任务完成")
        logger.info("=" * 60)

        result["status"] = "success"
        return result

    except Exception as e:
        logger.error(f"GPU 测试任务失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "task_id": self.request.id,
        }


@celery_app.task(bind=True, name="app.tasks.training_tasks.test_queue_isolation")
def test_queue_isolation(self: Task, task_number: int = 1) -> dict:
    """
    队列隔离测试任务
    用于验证 training 队列不会阻塞其他队列

    Args:
        task_number: 任务编号

    Returns:
        dict: 测试结果
    """
    try:
        logger.info(f"队列隔离测试任务 #{task_number} 开始")
        logger.info(f"Task ID: {self.request.id}")
        logger.info(f"Queue: {self.request.delivery_info.get('routing_key', 'unknown')}")

        # 模拟长时间运行的任务（15秒）
        total_steps = 15
        for i in range(total_steps):
            time.sleep(1)
            progress = int((i + 1) / total_steps * 100)
            logger.info(f"任务 #{task_number} 进度: {progress}%")
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'task_number': task_number,
                    'status': f'任务 #{task_number} 运行中 {progress}%'
                }
            )

        result = {
            "status": "success",
            "task_id": self.request.id,
            "task_number": task_number,
            "queue": self.request.delivery_info.get('routing_key', 'unknown'),
            "duration_seconds": total_steps,
        }

        logger.info(f"队列隔离测试任务 #{task_number} 完成")
        return result

    except Exception as e:
        logger.error(f"队列隔离测试任务 #{task_number} 失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "task_id": self.request.id,
            "task_number": task_number,
        }


# ============ 实际的训练任务 ============

import os
import shutil
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.crud.training import crud_training_job
from app.crud.ml_model import get_model_by_id, create_model
from app.services.data_preparation import DataPreparationService
from app.utils.yolo_trainer import YOLOTrainer


@celery_app.task(name="start_training", bind=True, max_retries=0)
def start_training_task(self, job_id: int) -> Dict[str, Any]:
    """
    异步训练任务

    Args:
        job_id: 训练任务 ID

    Returns:
        任务执行结果
    """
    logger.info(f"开始训练任务: job_id={job_id}")

    try:
        import asyncio
        result = asyncio.run(_start_training_async(job_id))
        return result

    except Exception as e:
        logger.error(f"训练任务失败: job_id={job_id}, error={str(e)}", exc_info=True)

        # 更新训练任务状态为失败
        try:
            import asyncio
            asyncio.run(_update_job_error(job_id, str(e)))
        except Exception as update_error:
            logger.error(f"更新训练错误状态失败: {str(update_error)}")

        # 不重试训练任务（耗时太长）
        raise


async def _start_training_async(job_id: int) -> Dict[str, Any]:
    """
    异步训练的内部方法

    Args:
        job_id: 训练任务 ID

    Returns:
        训练结果
    """
    async for db in get_db():
        try:
            # ========== 1. 获取训练任务 ==========
            job = await crud_training_job.get(db, job_id)
            if not job:
                raise ValueError(f"训练任务不存在: {job_id}")

            logger.info(f"训练任务信息: {job.job_name}, status={job.status}")

            # ========== 2. 获取基础模型 ==========
            base_model = await get_model_by_id(db, job.base_model_id)
            if not base_model:
                raise ValueError(f"基础模型不存在: {job.base_model_id}")

            if not base_model.model_path or not os.path.exists(base_model.model_path):
                raise ValueError(f"基础模型文件不存在: {base_model.model_path}")

            logger.info(f"基础模型: {base_model.model_name}, path={base_model.model_path}")

            # ========== 3. 更新状态为 preparing ==========
            await crud_training_job.update_status(
                db=db,
                job_id=job_id,
                status='preparing'
            )
            logger.info(f"训练状态更新为 preparing: job_id={job_id}")

            # ========== 4. 准备数据集 ==========
            from app.schemas.training import DatasetConfig

            dataset_config = DatasetConfig(**job.dataset_config)

            # 创建数据准备服务
            data_service = DataPreparationService(
                job_id=job_id,
                output_dir='storage/training'
            )

            logger.info(f"开始准备数据集...")
            dataset_result = await data_service.prepare_dataset(db, dataset_config)

            logger.info(
                f"数据集准备完成: train={dataset_result.train_count}, "
                f"val={dataset_result.val_count}, test={dataset_result.test_count}"
            )

            # ========== 5. 更新状态为 training ==========
            await crud_training_job.update_status(
                db=db,
                job_id=job_id,
                status='training'
            )
            logger.info(f"训练状态更新为 training: job_id={job_id}")

            # ========== 6. 执行训练 ==========
            from app.schemas.training import TrainingConfig

            training_config = TrainingConfig(**job.config_json)

            # 创建日志文件路径
            log_dir = Path('storage/training/logs')
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"training_job_{job_id}.log"

            # 创建训练器
            trainer = YOLOTrainer(log_file=str(log_file))

            logger.info(f"开始 YOLO 训练...")
            training_result = trainer.train(
                base_model=base_model.model_path,
                data_yaml=dataset_result.data_yaml_path,
                config=training_config.model_dump(),
                progress_callback=None  # TODO: 可以添加进度回调
            )

            if not training_result.get('success'):
                error_msg = training_result.get('error', 'Unknown error')
                raise RuntimeError(f"YOLO 训练失败: {error_msg}")

            logger.info(f"YOLO 训练完成!")

            # ========== 7. 复制权重文件到存储目录 ==========
            weights_dir = Path('storage/training/weights') / f"job_{job_id}"
            weights_dir.mkdir(parents=True, exist_ok=True)

            best_weights_src = Path(training_result['best_weights'])
            best_weights_dst = weights_dir / f"best_job_{job_id}.pt"

            shutil.copy(best_weights_src, best_weights_dst)
            logger.info(f"权重文件已复制: {best_weights_dst}")

            # ========== 8. 更新训练指标 ==========
            metrics = training_result.get('metrics', {})
            await crud_training_job.update_metrics(
                db=db,
                job_id=job_id,
                metrics=metrics
            )
            logger.info(f"训练指标已更新: {metrics}")

            # ========== 9. 注册新模型 ==========
            new_model = await create_model(
                db=db,
                model_name=f"{job.job_name}_trained",
                model_type=base_model.model_type,
                model_path=str(best_weights_dst),
                version=f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                description=f"从训练任务 {job_id} 生成的模型",
                performance_metrics=metrics
            )
            logger.info(f"新模型已注册: id={new_model.id}, name={new_model.model_name}")

            # ========== 10. 更新训练任务状态为 completed ==========
            await crud_training_job.update_status(
                db=db,
                job_id=job_id,
                status='completed',
                new_model_id=new_model.id,
                weights_path=str(best_weights_dst),
                results_path=training_result.get('results_dir'),
                log_file_path=str(log_file),
                current_epoch=training_config.epochs,
                total_epochs=training_config.epochs,
                progress_percentage=100.0
            )

            logger.info(f"训练任务完成: job_id={job_id}")

            return {
                'job_id': job_id,
                'status': 'completed',
                'new_model_id': new_model.id,
                'weights_path': str(best_weights_dst),
                'metrics': metrics,
                'dataset_info': {
                    'train_count': dataset_result.train_count,
                    'val_count': dataset_result.val_count,
                    'test_count': dataset_result.test_count
                }
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"训练过程出错: {str(e)}", exc_info=True)
            raise


async def _update_job_error(job_id: int, error_message: str):
    """
    更新训练任务错误状态

    Args:
        job_id: 训练任务 ID
        error_message: 错误信息
    """
    async for db in get_db():
        try:
            job = await crud_training_job.get(db, job_id)
            if job:
                await crud_training_job.update_status(
                    db=db,
                    job_id=job_id,
                    status='failed',
                    error_message=error_message
                )
                logger.info(f"训练错误状态已更新: job_id={job_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"更新训练错误状态失败: {str(e)}", exc_info=True)
            raise
