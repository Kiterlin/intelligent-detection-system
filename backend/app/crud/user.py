"""
用户 CRUD 操作
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    根据 ID 获取用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    根据用户名获取用户

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    根据邮箱获取用户

    Args:
        db: 数据库会话
        email: 电子邮箱

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate, role: UserRole = UserRole.USER) -> User:
    """
    创建新用户

    Args:
        db: 数据库会话
        user_in: 用户创建数据
        role: 用户角色（默认为普通用户）

    Returns:
        User: 创建的用户对象

    Raises:
        ValueError: 用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user_in.username)
    if existing_user:
        raise ValueError("用户名已存在")

    # 检查邮箱是否已存在
    existing_email = await get_user_by_email(db, user_in.email)
    if existing_email:
        raise ValueError("邮箱已被注册")

    # 创建用户
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=role,
    )

    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建用户失败：数据冲突")


async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """
    更新用户信息

    Args:
        db: 数据库会话
        user_id: 用户 ID
        user_in: 用户更新数据

    Returns:
        Optional[User]: 更新后的用户对象，不存在则返回 None
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # 更新字段
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def update_password(db: AsyncSession, user_id: int, new_password: str) -> Optional[User]:
    """
    更新用户密码

    Args:
        db: 数据库会话
        user_id: 用户 ID
        new_password: 新密码（明文）

    Returns:
        Optional[User]: 更新后的用户对象，不存在则返回 None
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    删除用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        bool: 是否删除成功
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    await db.delete(user)
    await db.commit()
    return True


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[User]:
    """
    获取用户列表

    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        list[User]: 用户列表
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_users_with_filter(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
) -> tuple[list[User], int]:
    """
    获取用户列表（支持搜索和筛选）

    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        search: 搜索关键词（搜索用户名、邮箱）
        role: 角色筛选

    Returns:
        (用户列表, 总数) 元组
    """
    query = select(User)

    # 搜索条件
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # 角色筛选
    if role:
        query = query.where(User.role == role)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页查询
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = list(result.scalars().all())

    return users, total or 0


async def batch_delete_users(db: AsyncSession, user_ids: list[int]) -> int:
    """
    批量删除用户

    Args:
        db: 数据库会话
        user_ids: 用户ID列表

    Returns:
        删除的用户数量
    """
    result = await db.execute(
        delete(User).where(User.id.in_(user_ids))
    )
    await db.commit()
    return result.rowcount


async def batch_update_user_status(
    db: AsyncSession, user_ids: list[int], is_active: bool
) -> int:
    """
    批量更新用户状态

    Args:
        db: 数据库会话
        user_ids: 用户ID列表
        is_active: 激活状态

    Returns:
        更新的用户数量
    """
    stmt = select(User).where(User.id.in_(user_ids))
    result = await db.execute(stmt)
    users = result.scalars().all()

    count = 0
    for user in users:
        user.is_active = is_active
        count += 1

    await db.commit()
    return count
