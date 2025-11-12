"""
Celery应用实例
用于异步任务处理（视频检测等耗时任务）
"""
from celery import Celery
from app.core.config import settings

# 创建Celery应用实例
celery_app = Celery(
    "water_detection",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery配置
celery_app.conf.update(
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    result_expires=settings.CELERY_RESULT_EXPIRES,
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,  # 任务执行完成后才确认
    worker_prefetch_multiplier=1,  # 每次只预取1个任务（适合耗时任务）
)

# 自动发现任务模块
celery_app.autodiscover_tasks(["app.tasks"])
