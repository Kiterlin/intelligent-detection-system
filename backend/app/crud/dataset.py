"""
数据集 CRUD 操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.dataset import Dataset, DataFile, BatchJob, BatchJobStatus


# ==================== 数据集 CRUD ====================

async def create_dataset(
    db: AsyncSession,
    name: str,
    user_id: int,
    description: Optional[str] = None,
) -> Dataset:
    """
    创建新数据集

    Args:
        db: 数据库会话
        name: 数据集名称
        user_id: 创建者ID
        description: 数据集描述

    Returns:
        Dataset: 创建的数据集对象

    Raises:
        ValueError: 创建失败
    """
    db_dataset = Dataset(
        name=name,
        user_id=user_id,
        description=description,
    )

    db.add(db_dataset)
    try:
        await db.commit()
        await db.refresh(db_dataset)
        return db_dataset
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建数据集失败：数据冲突")


async def get_dataset_by_id(
    db: AsyncSession, dataset_id: int, user_id: Optional[int] = None
) -> Optional[Dataset]:
    """
    根据ID获取数据集

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        user_id: 用户ID（如果提供，验证所有权）

    Returns:
        Optional[Dataset]: 数据集对象，不存在则返回None
    """
    query = select(Dataset).where(Dataset.id == dataset_id)

    # 如果提供了user_id，验证所有权
    if user_id is not None:
        query = query.where(Dataset.user_id == user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_datasets(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> tuple[List[Dataset], int]:
    """
    获取用户数据集列表

    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        search: 搜索关键词（搜索名称和描述）

    Returns:
        (数据集列表, 总数) 元组
    """
    query = select(Dataset).where(Dataset.user_id == user_id)
    count_query = select(func.count(Dataset.id)).where(Dataset.user_id == user_id)

    # 搜索过滤
    if search:
        search_filter = or_(
            Dataset.name.ilike(f"%{search}%"),
            Dataset.description.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按创建时间倒序
    query = query.offset(skip).limit(limit).order_by(Dataset.created_at.desc())

    # 使用 selectinload 预加载文件关系以提高性能
    query = query.options(selectinload(Dataset.files))

    result = await db.execute(query)
    datasets = list(result.scalars().all())

    return datasets, total


async def get_dataset_with_files(
    db: AsyncSession, dataset_id: int, user_id: Optional[int] = None
) -> Optional[Dataset]:
    """
    获取数据集及其所有文件

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        user_id: 用户ID（如果提供，验证所有权）

    Returns:
        Optional[Dataset]: 数据集对象（包含文件列表），不存在则返回None
    """
    query = (
        select(Dataset)
        .where(Dataset.id == dataset_id)
        .options(selectinload(Dataset.files))
    )

    if user_id is not None:
        query = query.where(Dataset.user_id == user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_dataset(
    db: AsyncSession,
    dataset_id: int,
    user_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Dataset]:
    """
    更新数据集信息

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        user_id: 用户ID（验证所有权）
        name: 新名称
        description: 新描述

    Returns:
        Optional[Dataset]: 更新后的数据集对象，不存在或无权限则返回None
    """
    dataset = await get_dataset_by_id(db, dataset_id, user_id)
    if not dataset:
        return None

    if name is not None:
        dataset.name = name
    if description is not None:
        dataset.description = description

    dataset.updated_at = datetime.now()

    await db.commit()
    await db.refresh(dataset)
    return dataset


async def delete_dataset(db: AsyncSession, dataset_id: int, user_id: int) -> bool:
    """
    删除数据集（级联删除文件和任务）

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        user_id: 用户ID（验证所有权）

    Returns:
        bool: 是否删除成功
    """
    dataset = await get_dataset_by_id(db, dataset_id, user_id)
    if not dataset:
        return False

    await db.delete(dataset)
    await db.commit()
    return True


# ==================== 数据文件 CRUD ====================

async def add_file_to_dataset(
    db: AsyncSession,
    dataset_id: int,
    filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
) -> DataFile:
    """
    添加文件到数据集

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        filename: 文件名
        file_path: 文件路径
        file_size: 文件大小（字节）
        file_type: 文件类型（image/video）

    Returns:
        DataFile: 创建的文件对象

    Raises:
        ValueError: 创建失败
    """
    db_file = DataFile(
        dataset_id=dataset_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
    )

    db.add(db_file)
    try:
        await db.commit()
        await db.refresh(db_file)
        return db_file
    except IntegrityError:
        await db.rollback()
        raise ValueError("添加文件失败：数据冲突")


async def get_dataset_files(
    db: AsyncSession,
    dataset_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[DataFile], int]:
    """
    获取数据集文件列表

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        (文件列表, 总数) 元组
    """
    query = select(DataFile).where(DataFile.dataset_id == dataset_id)
    count_query = select(func.count(DataFile.id)).where(DataFile.dataset_id == dataset_id)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按上传时间倒序
    query = query.offset(skip).limit(limit).order_by(DataFile.uploaded_at.desc())
    result = await db.execute(query)
    files = list(result.scalars().all())

    return files, total


async def get_file_by_id(
    db: AsyncSession, file_id: int
) -> Optional[DataFile]:
    """
    根据ID获取文件

    Args:
        db: 数据库会话
        file_id: 文件ID

    Returns:
        Optional[DataFile]: 文件对象，不存在则返回None
    """
    result = await db.execute(
        select(DataFile).where(DataFile.id == file_id)
    )
    return result.scalar_one_or_none()


async def delete_file(db: AsyncSession, file_id: int) -> bool:
    """
    删除文件

    Args:
        db: 数据库会话
        file_id: 文件ID

    Returns:
        bool: 是否删除成功
    """
    file_obj = await get_file_by_id(db, file_id)
    if not file_obj:
        return False

    await db.delete(file_obj)
    await db.commit()
    return True


# ==================== 批量任务 CRUD ====================

async def create_batch_job(
    db: AsyncSession,
    dataset_id: int,
    user_id: int,
    model_id: int,
    total_files: int,
    confidence_threshold: float,
    iou_threshold: float,
    celery_group_id: Optional[str] = None,
) -> BatchJob:
    """
    创建批量检测任务

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        user_id: 用户ID
        model_id: 模型ID
        total_files: 总文件数
        confidence_threshold: 置信度阈值
        iou_threshold: IOU阈值
        celery_group_id: Celery Group 任务ID

    Returns:
        BatchJob: 创建的批量任务对象

    Raises:
        ValueError: 创建失败
    """
    db_job = BatchJob(
        dataset_id=dataset_id,
        user_id=user_id,
        model_id=model_id,
        total_files=total_files,
        confidence_threshold=str(confidence_threshold),
        iou_threshold=str(iou_threshold),
        celery_group_id=celery_group_id,
        status=BatchJobStatus.PENDING,
    )

    db.add(db_job)
    try:
        await db.commit()
        await db.refresh(db_job)
        return db_job
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建批量任务失败：数据冲突")


async def get_batch_job_by_id(
    db: AsyncSession, job_id: int, user_id: Optional[int] = None
) -> Optional[BatchJob]:
    """
    根据ID获取批量任务

    Args:
        db: 数据库会话
        job_id: 任务ID
        user_id: 用户ID（如果提供，验证所有权）

    Returns:
        Optional[BatchJob]: 批量任务对象，不存在则返回None
    """
    query = (
        select(BatchJob)
        .where(BatchJob.id == job_id)
        .options(
            selectinload(BatchJob.dataset),
            selectinload(BatchJob.model)
        )
    )

    if user_id is not None:
        query = query.where(BatchJob.user_id == user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_batch_jobs(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    status: Optional[BatchJobStatus] = None,
) -> tuple[List[BatchJob], int]:
    """
    获取用户批量任务列表

    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        status: 状态过滤

    Returns:
        (任务列表, 总数) 元组
    """
    query = select(BatchJob).where(BatchJob.user_id == user_id)
    count_query = select(func.count(BatchJob.id)).where(BatchJob.user_id == user_id)

    # 状态过滤
    if status:
        query = query.where(BatchJob.status == status)
        count_query = count_query.where(BatchJob.status == status)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按创建时间倒序
    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(BatchJob.created_at.desc())
        .options(
            selectinload(BatchJob.dataset),
            selectinload(BatchJob.model)
        )
    )

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    return jobs, total


async def update_batch_job_status(
    db: AsyncSession,
    job_id: int,
    status: BatchJobStatus,
    error_message: Optional[str] = None,
) -> Optional[BatchJob]:
    """
    更新批量任务状态

    Args:
        db: 数据库会话
        job_id: 任务ID
        status: 新状态
        error_message: 错误信息（失败时提供）

    Returns:
        Optional[BatchJob]: 更新后的任务对象，不存在则返回None
    """
    job = await get_batch_job_by_id(db, job_id)
    if not job:
        return None

    job.status = status
    if error_message:
        job.error_message = error_message

    # 更新时间戳
    if status == BatchJobStatus.RUNNING and not job.started_at:
        job.started_at = datetime.now()
    elif status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED, BatchJobStatus.CANCELLED]:
        job.completed_at = datetime.now()

    await db.commit()
    await db.refresh(job)
    return job


async def update_batch_job_progress(
    db: AsyncSession,
    job_id: int,
    completed_files: Optional[int] = None,
    failed_files: Optional[int] = None,
) -> Optional[BatchJob]:
    """
    更新批量任务进度

    Args:
        db: 数据库会话
        job_id: 任务ID
        completed_files: 已完成文件数（增量）
        failed_files: 失败文件数（增量）

    Returns:
        Optional[BatchJob]: 更新后的任务对象，不存在则返回None
    """
    job = await get_batch_job_by_id(db, job_id)
    if not job:
        return None

    if completed_files is not None:
        job.completed_files += completed_files
    if failed_files is not None:
        job.failed_files += failed_files

    # 检查是否全部完成
    if job.completed_files + job.failed_files >= job.total_files:
        if job.failed_files == 0:
            job.status = BatchJobStatus.COMPLETED
        elif job.completed_files == 0:
            job.status = BatchJobStatus.FAILED
        else:
            job.status = BatchJobStatus.COMPLETED  # 部分成功也标记为完成
        job.completed_at = datetime.now()

    await db.commit()
    await db.refresh(job)
    return job


async def get_dataset_batch_jobs(
    db: AsyncSession,
    dataset_id: int,
    skip: int = 0,
    limit: int = 10,
) -> tuple[List[BatchJob], int]:
    """
    获取数据集的批量任务列表

    Args:
        db: 数据库会话
        dataset_id: 数据集ID
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        (任务列表, 总数) 元组
    """
    query = select(BatchJob).where(BatchJob.dataset_id == dataset_id)
    count_query = select(func.count(BatchJob.id)).where(BatchJob.dataset_id == dataset_id)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按创建时间倒序
    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(BatchJob.created_at.desc())
        .options(selectinload(BatchJob.model))
    )

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    return jobs, total
