"""
训练任务相关的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.training import TrainingJob
from app.schemas.training import TrainingJobCreate, TrainingJobUpdate


class CRUDTrainingJob:
    """训练任务 CRUD 操作"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TrainingJobCreate,
        admin_id: int
    ) -> TrainingJob:
        """创建训练任务"""
        db_obj = TrainingJob(
            admin_id=admin_id,
            job_name=obj_in.job_name,
            base_model_id=obj_in.base_model_id,
            config_json=obj_in.config_json.model_dump(),
            dataset_config=obj_in.dataset_config.model_dump(),
            total_epochs=obj_in.config_json.epochs,
            status='pending'
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, job_id: int) -> Optional[TrainingJob]:
        """获取单个训练任务"""
        result = await db.execute(
            select(TrainingJob).where(TrainingJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        admin_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> tuple[List[TrainingJob], int]:
        """获取多个训练任务（分页）"""
        # 构建查询
        query = select(TrainingJob)

        # 过滤条件
        if admin_id is not None:
            query = query.where(TrainingJob.admin_id == admin_id)
        if status is not None:
            query = query.where(TrainingJob.status == status)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.offset(skip).limit(limit).order_by(TrainingJob.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: TrainingJob,
        obj_in: TrainingJobUpdate
    ) -> TrainingJob:
        """更新训练任务"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_status(
        self,
        db: AsyncSession,
        *,
        job_id: int,
        status: str,
        **kwargs
    ) -> TrainingJob:
        """更新训练任务状态"""
        job = await self.get(db, job_id)
        if not job:
            raise ValueError(f"Training job {job_id} not found")

        job.status = status

        # 更新其他字段
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        # 根据状态自动设置时间戳
        if status == 'training' and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ['completed', 'failed', 'cancelled'] and not job.completed_at:
            job.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(job)
        return job

    async def update_progress(
        self,
        db: AsyncSession,
        *,
        job_id: int,
        current_epoch: int,
        total_epochs: int
    ) -> TrainingJob:
        """更新训练进度"""
        job = await self.get(db, job_id)
        if not job:
            raise ValueError(f"Training job {job_id} not found")

        job.current_epoch = current_epoch
        job.total_epochs = total_epochs
        job.progress_percentage = (current_epoch / total_epochs * 100) if total_epochs > 0 else 0

        await db.commit()
        await db.refresh(job)
        return job

    async def update_metrics(
        self,
        db: AsyncSession,
        *,
        job_id: int,
        metrics: Dict[str, Any]
    ) -> TrainingJob:
        """更新训练指标"""
        job = await self.get(db, job_id)
        if not job:
            raise ValueError(f"Training job {job_id} not found")

        job.metrics_json = metrics

        await db.commit()
        await db.refresh(job)
        return job

    async def delete(self, db: AsyncSession, *, job_id: int) -> bool:
        """删除训练任务"""
        result = await db.execute(
            select(TrainingJob).where(TrainingJob.id == job_id)
        )
        db_obj = result.scalar_one_or_none()

        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False

    async def get_active_jobs(
        self,
        db: AsyncSession
    ) -> List[TrainingJob]:
        """获取所有活跃的训练任务（preparing, training 状态）"""
        result = await db.execute(
            select(TrainingJob).where(
                TrainingJob.status.in_(['preparing', 'training'])
            ).order_by(TrainingJob.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_completed_jobs_count(
        self,
        db: AsyncSession,
        admin_id: Optional[int] = None
    ) -> int:
        """获取已完成的训练任务数量"""
        query = select(func.count(TrainingJob.id)).where(
            TrainingJob.status == 'completed'
        )

        if admin_id is not None:
            query = query.where(TrainingJob.admin_id == admin_id)

        result = await db.execute(query)
        return result.scalar() or 0


# 创建 CRUD 实例
crud_training_job = CRUDTrainingJob()
