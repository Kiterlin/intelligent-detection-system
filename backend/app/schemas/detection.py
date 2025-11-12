"""
检测相关的 Pydantic 模式
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.detection_history import DetectionInputType, DetectionStatus


# 检测请求基础模式
class DetectionBase(BaseModel):
    """检测请求基础模式"""

    confidence_threshold: Optional[float] = Field(
        0.25, ge=0.0, le=1.0, description="置信度阈值"
    )
    iou_threshold: Optional[float] = Field(0.45, ge=0.0, le=1.0, description="IOU阈值")


# 图像检测请求模式
class ImageDetectionRequest(DetectionBase):
    """图像检测请求模式"""

    pass


# 视频检测请求模式
class VideoDetectionRequest(DetectionBase):
    """视频检测请求模式"""

    pass


# 检测结果对象
class DetectionObject(BaseModel):
    """单个检测对象"""

    class_id: int = Field(..., description="类别ID")
    class_name: str = Field(..., description="类别名称")
    confidence: float = Field(..., description="置信度")
    bbox: List[float] = Field(..., description="边界框 [x1, y1, x2, y2]")


# 图像检测响应模式
class ImageDetectionResponse(BaseModel):
    """图像检测响应模式"""

    detection_id: int = Field(..., description="检测记录ID")
    objects: List[DetectionObject] = Field(..., description="检测到的对象列表")
    detected_count: int = Field(..., description="检测到的对象数量")
    processing_time: float = Field(..., description="处理时间（秒）")
    output_file_path: str = Field(..., description="标注后的图像路径")


# 视频检测响应模式
class VideoDetectionResponse(BaseModel):
    """视频检测响应模式"""

    task_id: str = Field(..., description="Celery任务ID")
    detection_id: int = Field(..., description="检测记录ID")
    message: str = Field(..., description="提示信息")


# 任务状态响应
class TaskStatusResponse(BaseModel):
    """任务状态响应模式"""

    task_id: str = Field(..., description="任务ID")
    status: DetectionStatus = Field(..., description="任务状态")
    detection_id: int = Field(..., description="检测记录ID")
    progress: Optional[float] = Field(None, description="进度百分比 (0-100)")
    message: Optional[str] = Field(None, description="状态信息")
    result: Optional[Dict[str, Any]] = Field(None, description="检测结果（完成时返回）")


# 检测历史响应模式
class DetectionHistoryResponse(BaseModel):
    """检测历史响应模式"""

    id: int
    user_id: int
    model_id: int
    input_type: DetectionInputType
    input_file_path: str
    output_file_path: Optional[str]
    result_json: Optional[str]
    detected_objects_count: int
    status: DetectionStatus
    task_id: Optional[str]
    processing_time: Optional[float]
    confidence_threshold: Optional[float]
    iou_threshold: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 检测历史列表响应模式
class DetectionHistoryListResponse(BaseModel):
    """检测历史列表响应模式"""

    histories: List[DetectionHistoryResponse]
    total: int
    page: int
    page_size: int


# 检测统计响应
class DetectionStatsResponse(BaseModel):
    """检测统计响应模式"""

    total_detections: int = Field(..., description="总检测次数")
    image_detections: int = Field(..., description="图像检测次数")
    video_detections: int = Field(..., description="视频检测次数")
    total_objects_detected: int = Field(..., description="总检测对象数")
    avg_processing_time: Optional[float] = Field(None, description="平均处理时间（秒）")
