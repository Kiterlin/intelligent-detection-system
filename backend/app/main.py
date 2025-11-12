"""
FastAPI 应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    应用启动时的事件处理
    """
    # 开发环境下自动创建表（生产环境使用 Alembic 迁移）
    await init_db()
    print("✅ Database initialized")
    print(f"📚 API Documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时的事件处理
    """
    print("👋 Shutting down...")


@app.get("/", tags=["Root"])
async def root():
    """
    根路径 - 返回 API 基本信息
    """
    return {
        "message": "Welcome to Water Target Detection API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


# TODO: 在 Stage 3 中添加 API 路由
# app.include_router(api_router, prefix=settings.API_V1_STR)
