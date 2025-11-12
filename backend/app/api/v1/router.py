"""
API v1 主路由
"""
from fastapi import APIRouter

from app.api.v1 import auth, admin

# 创建 API v1 路由器
api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册管理员路由
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])

# TODO: 在后续阶段添加其他路由
# api_router.include_router(detection.router, prefix="/detection", tags=["检测"])
