"""
认证相关 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.crud.user import (
    create_user,
    get_user_by_username,
    update_password,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    PasswordChange,
)
from app.schemas.token import Token
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册

    创建新的普通用户账号
    """
    try:
        user = await create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录

    验证用户名和密码，返回 JWT token
    """
    # 验证用户
    user = await get_user_by_username(db, user_in.username)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建 access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息

    需要认证
    """
    return current_user


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码

    需要认证，验证旧密码后更新为新密码
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    await update_password(db, current_user.id, password_data.new_password)

    return {"message": "密码修改成功"}
