"""
Celery 任务模块
"""
from app.tasks.detection import process_video_detection

__all__ = ["process_video_detection"]
