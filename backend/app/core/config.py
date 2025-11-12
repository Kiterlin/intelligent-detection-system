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

    # Redis配置（第三阶段使用）
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT配置
    SECRET_KEY: str = "your_secret_key_here_please_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    RESULT_DIR: str = "results"
    MODEL_DIR: str = "models"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
