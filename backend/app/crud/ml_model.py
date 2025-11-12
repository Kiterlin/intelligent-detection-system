"""
机器学习模型 CRUD 操作
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from sqlalchemy.exc import IntegrityError

from app.models.ml_model import MLModel, ModelStatus
from app.utils.file import delete_file


async def get_model_by_id(db: AsyncSession, model_id: int) -> Optional[MLModel]:
    """
    根据ID获取模型

    Args:
        db: 数据库会话
        model_id: 模型ID

    Returns:
        Optional[MLModel]: 模型对象，不存在则返回None
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    return result.scalar_one_or_none()


async def get_models_with_filter(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[ModelStatus] = None,
) -> tuple[list[MLModel], int]:
    """
    获取模型列表（支持搜索和筛选）

    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        search: 搜索关键词（搜索模型名称、版本）
        status: 状态筛选

    Returns:
        (模型列表, 总数) 元组
    """
    query = select(MLModel)

    # 搜索条件
    if search:
        search_filter = or_(
            MLModel.name.ilike(f"%{search}%"),
            MLModel.version.ilike(f"%{search}%"),
            MLModel.description.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # 状态筛选
    if status:
        query = query.where(MLModel.status == status)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页查询
    query = query.offset(skip).limit(limit).order_by(MLModel.created_at.desc())
    result = await db.execute(query)
    models = list(result.scalars().all())

    return models, total or 0


async def create_model(
    db: AsyncSession,
    name: str,
    filename: str,
    file_path: str,
    file_size: int,
    uploaded_by: int,
    version: Optional[str] = None,
    description: Optional[str] = None,
) -> MLModel:
    """
    创建新模型记录

    Args:
        db: 数据库会话
        name: 模型名称
        filename: 原始文件名
        file_path: 文件存储路径
        file_size: 文件大小
        uploaded_by: 上传者ID
        version: 模型版本
        description: 模型描述

    Returns:
        MLModel: 创建的模型对象

    Raises:
        ValueError: 创建失败
    """
    db_model = MLModel(
        name=name,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        uploaded_by=uploaded_by,
        version=version,
        description=description,
        status=ModelStatus.INACTIVE,  # 默认为停用状态
    )

    db.add(db_model)
    try:
        await db.commit()
        await db.refresh(db_model)
        return db_model
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建模型失败：数据冲突")


async def update_model(
    db: AsyncSession,
    model_id: int,
    name: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[MLModel]:
    """
    更新模型信息

    Args:
        db: 数据库会话
        model_id: 模型ID
        name: 模型名称
        version: 模型版本
        description: 模型描述

    Returns:
        Optional[MLModel]: 更新后的模型对象，不存在则返回None
    """
    model = await get_model_by_id(db, model_id)
    if not model:
        return None

    # 更新字段
    if name is not None:
        model.name = name
    if version is not None:
        model.version = version
    if description is not None:
        model.description = description

    await db.commit()
    await db.refresh(model)
    return model


async def update_model_status(
    db: AsyncSession, model_id: int, status: ModelStatus
) -> Optional[MLModel]:
    """
    更新模型状态

    Args:
        db: 数据库会话
        model_id: 模型ID
        status: 新状态

    Returns:
        Optional[MLModel]: 更新后的模型对象，不存在则返回None
    """
    model = await get_model_by_id(db, model_id)
    if not model:
        return None

    # 如果要激活此模型，先停用所有其他模型（确保只有一个激活的模型）
    if status == ModelStatus.ACTIVE:
        await db.execute(
            select(MLModel)
            .where(MLModel.status == ModelStatus.ACTIVE)
            .where(MLModel.id != model_id)
        )
        active_models_result = await db.execute(
            select(MLModel).where(MLModel.status == ModelStatus.ACTIVE)
        )
        for active_model in active_models_result.scalars().all():
            active_model.status = ModelStatus.INACTIVE

    model.status = status
    await db.commit()
    await db.refresh(model)
    return model


async def delete_model(db: AsyncSession, model_id: int) -> bool:
    """
    删除模型及其文件

    Args:
        db: 数据库会话
        model_id: 模型ID

    Returns:
        bool: 是否删除成功
    """
    model = await get_model_by_id(db, model_id)
    if not model:
        return False

    # 删除文件
    delete_file(model.file_path)

    # 删除数据库记录
    await db.delete(model)
    await db.commit()
    return True


async def get_active_model(db: AsyncSession) -> Optional[MLModel]:
    """
    获取当前激活的模型

    Args:
        db: 数据库会话

    Returns:
        Optional[MLModel]: 激活的模型，不存在则返回None
    """
    result = await db.execute(
        select(MLModel).where(MLModel.status == ModelStatus.ACTIVE)
    )
    return result.scalar_one_or_none()


async def get_model_count(db: AsyncSession) -> int:
    """
    获取模型总数

    Args:
        db: 数据库会话

    Returns:
        int: 模型总数
    """
    result = await db.scalar(select(func.count(MLModel.id)))
    return result or 0
