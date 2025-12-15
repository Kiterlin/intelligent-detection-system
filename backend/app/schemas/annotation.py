"""
标注相关的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============ AnnotationTask Schemas ============

class AnnotationTaskBase(BaseModel):
    """标注任务基础 schema"""
    name: str = Field(..., min_length=1, max_length=255, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    dataset_id: Optional[int] = Field(None, description="关联的数据集 ID")
    detection_history_id: Optional[int] = Field(None, description="关联的检测记录 ID")
    class_labels: Optional[List[str]] = Field(None, description="类别标签列表")
    requires_review: bool = Field(False, description="是否需要审核")


class AnnotationTaskCreate(AnnotationTaskBase):
    """创建标注任务的 schema"""
    pass


class AnnotationTaskUpdate(BaseModel):
    """更新标注任务的 schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|archived)$")
    is_published: Optional[bool] = None
    requires_review: Optional[bool] = None


class AnnotationTaskInDB(AnnotationTaskBase):
    """数据库中的标注任务 schema"""
    id: int
    label_studio_project_id: Optional[int] = None
    label_studio_project_url: Optional[str] = None
    labeling_config: Optional[str] = None
    status: str
    total_tasks: int = 0
    completed_tasks: int = 0
    progress: int = 0
    is_published: bool = False
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotationTaskResponse(AnnotationTaskInDB):
    """API 返回的标注任务 schema（包含统计信息）"""
    annotation_count: Optional[int] = Field(0, description="标注记录数")
    pending_count: Optional[int] = Field(0, description="待标注数")
    annotated_count: Optional[int] = Field(0, description="已标注数")


# ============ Annotation Schemas ============

class AnnotationBase(BaseModel):
    """标注记录基础 schema"""
    image_path: str = Field(..., min_length=1, max_length=500)
    image_name: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None


class AnnotationCreate(AnnotationBase):
    """创建标注记录的 schema"""
    task_id: int
    predictions_data: Optional[Dict[str, Any]] = Field(None, description="预标注数据")


class AnnotationUpdate(BaseModel):
    """更新标注记录的 schema"""
    annotations_data: Optional[Dict[str, Any]] = Field(None, description="标注数据")
    status: Optional[str] = Field(None, pattern="^(pending|annotated|verified|rejected)$")
    object_count: Optional[int] = None
    annotation_time_seconds: Optional[int] = None
    quality_score: Optional[int] = Field(None, ge=0, le=100)
    is_difficult: Optional[bool] = None
    is_verified: Optional[bool] = None


class AnnotationInDB(AnnotationBase):
    """数据库中的标注记录 schema"""
    id: int
    task_id: int
    label_studio_task_id: Optional[int] = None
    label_studio_annotation_id: Optional[int] = None
    annotations_data: Optional[Dict[str, Any]] = None
    predictions_data: Optional[Dict[str, Any]] = None
    object_count: int = 0
    annotation_time_seconds: Optional[int] = None
    status: str
    quality_score: Optional[int] = None
    is_difficult: bool = False
    is_verified: bool = False
    annotated_by: Optional[int] = None
    verified_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    annotated_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotationResponse(AnnotationInDB):
    """API 返回的标注记录 schema"""
    pass


# ============ AnnotationExport Schemas ============

class AnnotationExportBase(BaseModel):
    """标注导出基础 schema"""
    export_format: str = Field(..., pattern="^(yolo|coco|label_studio_json)$", description="导出格式")
    export_options: Optional[Dict[str, Any]] = Field(None, description="导出选项")


class AnnotationExportCreate(AnnotationExportBase):
    """创建标注导出的 schema"""
    task_id: int


class AnnotationExportInDB(AnnotationExportBase):
    """数据库中的标注导出 schema"""
    id: int
    task_id: int
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    exported_count: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotationExportResponse(AnnotationExportInDB):
    """API 返回的标注导出 schema"""
    download_url: Optional[str] = None


# ============ List/Pagination Schemas ============

class AnnotationTaskListResponse(BaseModel):
    """标注任务列表响应"""
    total: int
    items: List[AnnotationTaskResponse]


class AnnotationListResponse(BaseModel):
    """标注记录列表响应"""
    total: int
    items: List[AnnotationResponse]


# ============ Statistics Schemas ============

class AnnotationTaskStatistics(BaseModel):
    """标注任务统计 schema"""
    task_id: int
    task_name: str
    total_annotations: int
    pending_annotations: int
    annotated_annotations: int
    verified_annotations: int
    progress_percentage: float
    average_annotation_time: Optional[float] = None  # 秒
    average_quality_score: Optional[float] = None


class AnnotationOverviewStatistics(BaseModel):
    """标注整体统计 schema"""
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    total_annotations: int
    annotated_count: int
    verified_count: int
    overall_progress: float  # 百分比
