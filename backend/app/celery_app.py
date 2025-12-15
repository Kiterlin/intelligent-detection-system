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
    # 任务路由配置 - 将不同类型的任务分配到不同队列
    task_routes={
        'app.tasks.detection_tasks.*': {'queue': 'detection'},  # 检测任务使用detection队列
        'app.tasks.report_tasks.*': {'queue': 'reports'},  # 报告任务使用reports队列
        'app.tasks.training_tasks.*': {'queue': 'training'},  # 训练任务使用training队列
        'generate_report': {'queue': 'reports'},  # 报告生成任务
    },
    # 队列定义
    task_queues={
        'default': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'routing_key': 'default',
        },
        'detection': {
            'exchange': 'detection',
            'exchange_type': 'direct',
            'routing_key': 'detection',
        },
        'reports': {
            'exchange': 'reports',
            'exchange_type': 'direct',
            'routing_key': 'reports',
        },
        'training': {
            'exchange': 'training',
            'exchange_type': 'direct',
            'routing_key': 'training',
        },
    },
)

# 自动发现任务模块
celery_app.autodiscover_tasks(["app.tasks"])
