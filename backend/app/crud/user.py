"""
用户 CRUD 操作
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, ProfileUpdate
from app.core.security import get_password_hash
from app.core.cache import cache_manager, CacheKeys, invalidate_user_cache, invalidate_admin_stats_cache


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    根据 ID 获取用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    # 尝试从缓存获取
    cache_key = CacheKeys.user_info(user_id)
    cached_user = await cache_manager.get(cache_key)
    if cached_user:
        # 从缓存数据重建 User 对象（简化版，只返回基本信息）
        # 注意：实际使用时仍需从数据库获取完整对象
        pass

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # 缓存用户信息
    if user:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        await cache_manager.set(cache_key, user_dict, ttl=CacheKeys.TTL_USER_INFO)

    return user


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
        # 使管理后台统计缓存失效（用户数量变化）
        await invalidate_admin_stats_cache()
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
    # 使用户缓存失效
    await invalidate_user_cache(user_id)
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
    # 使用户缓存失效
    await invalidate_user_cache(user_id)
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
    # 使用户缓存和管理统计失效
    await invalidate_user_cache(user_id)
    await invalidate_admin_stats_cache()
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
    filters = []

    # 搜索条件
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    # 角色筛选
    if role:
        filters.append(User.role == role)

    # 应用筛选条件
    if filters:
        from sqlalchemy import and_
        query = query.where(and_(*filters))

    # 获取总数 - 使用优化的计数查询
    count_query = select(func.count(User.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    total = await db.scalar(count_query)

    # 分页查询 - 按创建时间倒序排序
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


async def update_profile(db: AsyncSession, user_id: int, profile_in: ProfileUpdate) -> Optional[User]:
    """
    更新用户个人信息

    Args:
        db: 数据库会话
        user_id: 用户 ID
        profile_in: 个人信息更新数据

    Returns:
        Optional[User]: 更新后的用户对象，不存在则返回 None

    Raises:
        ValueError: 邮箱已被使用
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # 如果要更新邮箱，检查邮箱是否被其他用户使用
    if profile_in.email and profile_in.email != user.email:
        existing_user = await get_user_by_email(db, profile_in.email)
        if existing_user and existing_user.id != user_id:
            raise ValueError("邮箱已被其他用户使用")

    # 更新字段（排除未设置的字段）
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    # 使用户缓存失效
    await invalidate_user_cache(user_id)
    return user


async def update_avatar(db: AsyncSession, user_id: int, avatar_url: str) -> Optional[User]:
    """
    更新用户头像

    Args:
        db: 数据库会话
        user_id: 用户 ID
        avatar_url: 头像 URL

    Returns:
        Optional[User]: 更新后的用户对象，不存在则返回 None
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(user)
    # 使用户缓存失效
    await invalidate_user_cache(user_id)
    return user
