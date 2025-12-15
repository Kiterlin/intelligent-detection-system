"""
Celery 任务模块
"""
from app.tasks.detection import process_video_detection
from app.tasks.annotation_tasks import (
    export_annotations_yolo_task,
    export_annotations_coco_task,
    export_annotations_label_studio_task
)
from app.tasks.training_tasks import start_training_task

__all__ = [
    "process_video_detection",
    "export_annotations_yolo_task",
    "export_annotations_coco_task",
    "export_annotations_label_studio_task",
    "start_training_task"
]
