"""
API v1 主路由
"""
from fastapi import APIRouter

from app.api.v1 import auth, admin, detect

# 创建 API v1 路由器
api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册管理员路由
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])

# 注册检测路由
api_router.include_router(detect.router, prefix="/detect", tags=["目标检测"])
