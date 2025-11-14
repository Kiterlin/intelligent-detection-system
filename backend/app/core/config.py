"""
应用配置模块
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 项目基本信息
    PROJECT_NAME: str = "Water Target Detection API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "企业级水下目标智能检测平台"
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./water_detection.db"
    DB_POOL_SIZE: int = 20  # 连接池大小
    DB_MAX_OVERFLOW: int = 10  # 连接池溢出大小
    DB_POOL_PRE_PING: bool = True  # 连接前检查连接有效性
    DB_ECHO: bool = False  # 生产环境关闭SQL日志，开发环境可设为True

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1小时任务超时
    CELERY_RESULT_EXPIRES: int = 86400  # 结果保留24小时

    # JWT配置
    SECRET_KEY: str = "your_secret_key_here_please_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    RESULT_DIR: str = "results"
    MODEL_DIR: str = "models"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # 检测配置
    DETECTION_INPUT_DIR: str = "uploads/detections/input"
    DETECTION_OUTPUT_DIR: str = "uploads/detections/output"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE: int = 200 * 1024 * 1024  # 200MB
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.25
    DEFAULT_IOU_THRESHOLD: float = 0.45
    SUPPORTED_IMAGE_FORMATS: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    SUPPORTED_VIDEO_FORMATS: List[str] = [".mp4", ".avi", ".mov", ".mkv"]

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
