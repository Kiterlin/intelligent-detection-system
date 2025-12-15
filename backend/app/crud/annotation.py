"""
标注相关的 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.annotation import AnnotationTask, Annotation, AnnotationExport
from app.schemas.annotation import (
    AnnotationTaskCreate,
    AnnotationTaskUpdate,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationExportCreate,
)


class CRUDAnnotationTask:
    """标注任务 CRUD 操作"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AnnotationTaskCreate,
        created_by: int
    ) -> AnnotationTask:
        """创建标注任务"""
        db_obj = AnnotationTask(
            **obj_in.model_dump(exclude_unset=True),
            created_by=created_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, task_id: int) -> Optional[AnnotationTask]:
        """获取单个标注任务"""
        result = await db.execute(
            select(AnnotationTask).where(AnnotationTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        created_by: Optional[int] = None,
        status: Optional[str] = None
    ) -> tuple[List[AnnotationTask], int]:
        """获取多个标注任务（分页）"""
        # 构建查询
        query = select(AnnotationTask)

        # 过滤条件
        if created_by is not None:
            query = query.where(AnnotationTask.created_by == created_by)
        if status is not None:
            query = query.where(AnnotationTask.status == status)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.offset(skip).limit(limit).order_by(AnnotationTask.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: AnnotationTask,
        obj_in: AnnotationTaskUpdate
    ) -> AnnotationTask:
        """更新标注任务"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, task_id: int) -> bool:
        """删除标注任务"""
        result = await db.execute(
            select(AnnotationTask).where(AnnotationTask.id == task_id)
        )
        db_obj = result.scalar_one_or_none()

        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False

    async def get_task_statistics(self, db: AsyncSession, task_id: int) -> dict:
        """获取标注任务统计信息"""
        # 获取各状态的标注数量
        stats_query = select(
            Annotation.status,
            func.count(Annotation.id).label('count')
        ).where(
            Annotation.task_id == task_id
        ).group_by(Annotation.status)

        result = await db.execute(stats_query)
        status_counts = {row.status: row.count for row in result.all()}

        # 获取总数
        total_result = await db.execute(
            select(func.count(Annotation.id)).where(Annotation.task_id == task_id)
        )
        total = total_result.scalar() or 0

        return {
            'annotation_count': total,
            'pending_count': status_counts.get('pending', 0),
            'annotated_count': status_counts.get('annotated', 0),
            'verified_count': status_counts.get('verified', 0),
        }


class CRUDAnnotation:
    """标注记录 CRUD 操作"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AnnotationCreate
    ) -> Annotation:
        """创建标注记录"""
        db_obj = Annotation(**obj_in.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, annotation_id: int) -> Optional[Annotation]:
        """获取单个标注记录"""
        result = await db.execute(
            select(Annotation).where(Annotation.id == annotation_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_task(
        self,
        db: AsyncSession,
        *,
        task_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> tuple[List[Annotation], int]:
        """获取任务的多个标注记录（分页）"""
        query = select(Annotation).where(Annotation.task_id == task_id)

        if status is not None:
            query = query.where(Annotation.status == status)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.offset(skip).limit(limit).order_by(Annotation.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Annotation,
        obj_in: AnnotationUpdate,
        annotated_by: Optional[int] = None
    ) -> Annotation:
        """更新标注记录"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # 如果更新标注数据，设置标注者
        if 'annotations_data' in update_data and annotated_by is not None:
            update_data['annotated_by'] = annotated_by

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, annotation_id: int) -> bool:
        """删除标注记录"""
        result = await db.execute(
            select(Annotation).where(Annotation.id == annotation_id)
        )
        db_obj = result.scalar_one_or_none()

        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False

    async def batch_create(
        self,
        db: AsyncSession,
        *,
        annotations: List[AnnotationCreate]
    ) -> List[Annotation]:
        """批量创建标注记录"""
        db_objs = [Annotation(**ann.model_dump(exclude_unset=True)) for ann in annotations]
        db.add_all(db_objs)
        await db.commit()

        # 刷新所有对象
        for obj in db_objs:
            await db.refresh(obj)

        return db_objs


class CRUDAnnotationExport:
    """标注导出 CRUD 操作"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AnnotationExportCreate,
        created_by: int
    ) -> AnnotationExport:
        """创建标注导出记录"""
        db_obj = AnnotationExport(
            **obj_in.model_dump(exclude_unset=True),
            created_by=created_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, export_id: int) -> Optional[AnnotationExport]:
        """获取单个导出记录"""
        result = await db.execute(
            select(AnnotationExport).where(AnnotationExport.id == export_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_task(
        self,
        db: AsyncSession,
        *,
        task_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[AnnotationExport], int]:
        """获取任务的多个导出记录（分页）"""
        query = select(AnnotationExport).where(AnnotationExport.task_id == task_id)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.offset(skip).limit(limit).order_by(AnnotationExport.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def update_status(
        self,
        db: AsyncSession,
        *,
        db_obj: AnnotationExport,
        status: str,
        file_path: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        exported_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> AnnotationExport:
        """更新导出状态"""
        db_obj.status = status

        if file_path is not None:
            db_obj.file_path = file_path
        if file_size_bytes is not None:
            db_obj.file_size_bytes = file_size_bytes
        if exported_count is not None:
            db_obj.exported_count = exported_count
        if error_message is not None:
            db_obj.error_message = error_message

        if status == 'completed':
            from datetime import datetime
            db_obj.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# 创建 CRUD 实例
crud_annotation_task = CRUDAnnotationTask()
crud_annotation = CRUDAnnotation()
crud_annotation_export = CRUDAnnotationExport()
