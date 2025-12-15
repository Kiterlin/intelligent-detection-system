"""
训练任务管理相关 API 端点
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.crud.training import crud_training_job
from app.schemas.training import (
    TrainingJobCreate,
    TrainingJobResponse,
    TrainingJobListResponse,
    TrainingJobUpdate,
)
from app.tasks.training_tasks import start_training_task
from loguru import logger

router = APIRouter()


# ==================== 辅助函数 ====================

def _build_job_response(job) -> TrainingJobResponse:
    """构建训练任务响应对象"""
    return TrainingJobResponse(
        id=job.id,
        admin_id=job.admin_id,
        base_model_id=job.base_model_id,
        new_model_id=job.new_model_id,
        job_name=job.job_name,
        status=job.status,
        config_json=job.config_json,
        dataset_config=job.dataset_config,
        log_file_path=job.log_file_path,
        weights_path=job.weights_path,
        results_path=job.results_path,
        metrics_json=job.metrics_json,
        current_epoch=job.current_epoch,
        total_epochs=job.total_epochs,
        progress_percentage=job.progress_percentage,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


# ==================== 训练任务管理端点 ====================

@router.post("/", response_model=TrainingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_training_job(
    job_data: TrainingJobCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    创建训练任务

    Args:
        job_data: 训练任务配置数据
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        创建的训练任务对象

    Raises:
        HTTPException: 创建失败

    需要管理员权限
    """
    try:
        # 1. 验证基础模型是否存在
        from app.crud.ml_model import get_model_by_id
        base_model = await get_model_by_id(db, job_data.base_model_id)
        if not base_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"基础模型不存在: {job_data.base_model_id}"
            )

        # 2. 如果使用标注数据，验证标注任务是否存在
        if job_data.dataset_config.source == 'annotations':
            if not job_data.dataset_config.annotation_task_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="使用标注数据时必须指定 annotation_task_id"
                )

            from app.crud.annotation import crud_annotation_task
            annotation_task = await crud_annotation_task.get(
                db, job_data.dataset_config.annotation_task_id
            )
            if not annotation_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"标注任务不存在: {job_data.dataset_config.annotation_task_id}"
                )

        # 3. 创建训练任务记录
        job = await crud_training_job.create(
            db=db,
            obj_in=job_data,
            admin_id=current_user.id
        )
        await db.commit()
        await db.refresh(job)

        logger.info(f"训练任务记录创建成功: job_id={job.id}, admin_id={current_user.id}")

        # 4. 触发异步训练任务
        task = start_training_task.delay(job.id)

        logger.info(f"训练任务已提交: job_id={job.id}, celery_task_id={task.id}")

        return _build_job_response(job)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"创建训练任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建训练任务失败: {str(e)}"
        )


@router.get("/", response_model=TrainingJobListResponse)
async def list_training_jobs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status_filter: Optional[str] = Query(None, description="按状态筛选"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取训练任务列表（分页）

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        status_filter: 状态筛选（pending/preparing/training/completed/failed/cancelled）
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        训练任务列表和总数

    需要管理员权限
    """
    try:
        # 查询训练任务列表
        jobs, total = await crud_training_job.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            status=status_filter
        )

        return TrainingJobListResponse(
            items=[_build_job_response(job) for job in jobs],
            total=total
        )

    except Exception as e:
        logger.error(f"获取训练任务列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取训练任务列表失败: {str(e)}"
        )


@router.get("/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取特定训练任务的详情

    Args:
        job_id: 训练任务ID
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        训练任务详情

    Raises:
        HTTPException: 任务不存在

    需要管理员权限
    """
    try:
        job = await crud_training_job.get(db, job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="训练任务不存在"
            )

        return _build_job_response(job)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练任务详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取训练任务详情失败: {str(e)}"
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    删除训练任务及其相关文件

    注意：只能删除已完成、失败或取消的任务，不能删除正在运行的任务

    Args:
        job_id: 训练任务ID
        current_user: 当前管理员用户
        db: 数据库会话

    Raises:
        HTTPException: 任务不存在或无法删除

    需要管理员权限
    """
    try:
        # 获取训练任务
        job = await crud_training_job.get(db, job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="训练任务不存在"
            )

        # 检查任务状态，不允许删除正在运行的任务
        if job.status in ['preparing', 'training']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除正在运行的训练任务，当前状态: {job.status}"
            )

        # 删除相关文件
        import shutil
        from pathlib import Path

        files_to_delete = []

        # 权重文件目录
        if job.weights_path:
            weights_dir = Path(job.weights_path).parent
            if weights_dir.exists():
                files_to_delete.append(weights_dir)

        # 结果目录
        if job.results_path and os.path.exists(job.results_path):
            files_to_delete.append(Path(job.results_path))

        # 日志文件
        if job.log_file_path and os.path.exists(job.log_file_path):
            files_to_delete.append(Path(job.log_file_path))

        # 数据集目录
        dataset_dir = Path('storage/training/datasets') / f"job_{job_id}"
        if dataset_dir.exists():
            files_to_delete.append(dataset_dir)

        # 删除文件
        for file_path in files_to_delete:
            try:
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    logger.info(f"已删除目录: {file_path}")
                else:
                    os.remove(file_path)
                    logger.info(f"已删除文件: {file_path}")
            except Exception as e:
                logger.warning(f"删除文件失败: {file_path}, error={str(e)}")

        # 删除数据库记录
        await crud_training_job.delete(db, job_id=job_id)
        await db.commit()

        logger.info(f"训练任务已删除: job_id={job_id}, admin_id={current_user.id}")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"删除训练任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除训练任务失败: {str(e)}"
        )


@router.get("/{job_id}/logs")
async def get_training_logs(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取训练日志文件内容

    Args:
        job_id: 训练任务ID
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        日志文件内容（文本流）

    Raises:
        HTTPException: 任务不存在或日志文件不可用

    需要管理员权限
    """
    try:
        # 获取训练任务
        job = await crud_training_job.get(db, job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="训练任务不存在"
            )

        # 检查日志文件
        if not job.log_file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志文件尚未生成"
            )

        if not os.path.exists(job.log_file_path):
            logger.error(f"日志文件不存在: {job.log_file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志文件不存在"
            )

        # 读取日志文件
        with open(job.log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()

        return {
            "job_id": job_id,
            "status": job.status,
            "log_content": log_content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取训练日志失败: {str(e)}"
        )


@router.get("/{job_id}/metrics")
async def get_training_metrics(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取训练性能指标

    Args:
        job_id: 训练任务ID
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        训练性能指标

    Raises:
        HTTPException: 任务不存在

    需要管理员权限
    """
    try:
        # 获取训练任务
        job = await crud_training_job.get(db, job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="训练任务不存在"
            )

        return {
            "job_id": job_id,
            "status": job.status,
            "current_epoch": job.current_epoch,
            "total_epochs": job.total_epochs,
            "progress_percentage": job.progress_percentage,
            "metrics": job.metrics_json
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练指标失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取训练指标失败: {str(e)}"
        )
