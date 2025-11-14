"""
认证相关 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.crud.user import (
    create_user,
    get_user_by_username,
    update_password,
    update_profile,
    update_avatar,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    PasswordChange,
    ProfileUpdate,
)
from app.schemas.token import Token
from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.file import save_upload_file, delete_file

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


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新个人信息

    需要认证，更新昵称、简介、手机号、邮箱等信息
    """
    try:
        updated_user = await update_profile(db, current_user.id, profile_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/upload-avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传用户头像

    需要认证，上传图片文件作为用户头像
    限制：图片格式（jpg, png, gif），大小不超过 2MB
    """
    # 允许的图片格式
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB

    try:
        # 如果已有头像，删除旧头像
        if current_user.avatar_url:
            delete_file(current_user.avatar_url)

        # 保存新头像
        avatar_path, file_size = await save_upload_file(
            file,
            "avatars",
            allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
            max_size=MAX_AVATAR_SIZE
        )

        # 更新用户头像 URL
        updated_user = await update_avatar(db, current_user.id, avatar_path)
        if not updated_user:
            # 如果更新失败，删除已上传的文件
            delete_file(avatar_path)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像上传失败: {str(e)}"
        )


@router.delete("/delete-avatar", response_model=UserResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户头像

    需要认证，删除当前用户的头像
    """
    if not current_user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户没有头像"
        )

    # 删除头像文件
    delete_file(current_user.avatar_url)

    # 更新数据库，清空头像 URL
    updated_user = await update_avatar(db, current_user.id, None)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return updated_user
