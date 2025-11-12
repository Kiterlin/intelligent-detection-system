"""
API v1 主路由
"""
from fastapi import APIRouter

from app.api.v1 import auth

# 创建 API v1 路由器
api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# TODO: 在后续阶段添加其他路由
# api_router.include_router(users.router, prefix="/users", tags=["用户"])
# api_router.include_router(detection.router, prefix="/detection", tags=["检测"])
# api_router.include_router(models.router, prefix="/models", tags=["模型"])
