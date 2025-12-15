"""
API v1 主路由
"""
from fastapi import APIRouter

from app.api.v1 import auth, admin, detect, dataset, alerts, comparison, reports, annotations, training

# 创建 API v1 路由器
api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册管理员路由
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])

# 注册检测路由
api_router.include_router(detect.router, prefix="/detect", tags=["目标检测"])

# 注册数据集路由
api_router.include_router(dataset.router, prefix="/datasets", tags=["数据集管理"])

# 注册告警路由
api_router.include_router(alerts.router, prefix="/alerts", tags=["告警系统"])

# 注册对比路由
api_router.include_router(comparison.router, prefix="/comparison", tags=["结果对比"])

# 注册报告路由
api_router.include_router(reports.router, prefix="/reports", tags=["报告生成"])

# 注册标注管理路由
api_router.include_router(annotations.router, prefix="/annotations", tags=["标注管理"])

# 注册训练管理路由
api_router.include_router(training.router, prefix="/training", tags=["模型训练"])
