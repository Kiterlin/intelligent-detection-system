"""
用户相关的 Pydantic 模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# 用户创建（注册）模式
class UserCreate(BaseModel):
    """用户注册请求模式"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="电子邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


# 用户更新模式
class UserUpdate(BaseModel):
    """用户更新请求模式"""

    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    is_active: Optional[bool] = Field(None, description="是否激活")
    role: Optional[UserRole] = Field(None, description="用户角色")


# 密码修改模式
class PasswordChange(BaseModel):
    """密码修改请求模式"""

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


# 用户登录模式
class UserLogin(BaseModel):
    """用户登录请求模式"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# 用户响应模式（不包含密码）
class UserResponse(BaseModel):
    """用户响应模式"""

    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 支持从 ORM 模型创建


# 用户列表响应模式
class UserListResponse(BaseModel):
    """用户列表响应模式"""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int
