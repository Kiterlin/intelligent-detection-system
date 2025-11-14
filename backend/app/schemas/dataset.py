"""
数据集相关的 Pydantic 模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.dataset import BatchJobStatus


# ==================== 数据集模式 ====================

class DatasetBase(BaseModel):
    """数据集基础模式"""

    name: str = Field(..., min_length=1, max_length=100, description="数据集名称")
    description: Optional[str] = Field(None, description="数据集描述")


class DatasetCreate(DatasetBase):
    """创建数据集请求模式"""

    pass


class DatasetUpdate(BaseModel):
    """更新数据集请求模式"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="数据集名称")
    description: Optional[str] = Field(None, description="数据集描述")


class DataFileResponse(BaseModel):
    """数据文件响应模式"""

    id: int
    dataset_id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DatasetResponse(BaseModel):
    """数据集响应模式"""

    id: int
    name: str
    description: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime

    # 统计信息（通过关联计算）
    file_count: int = Field(0, description="文件数量")
    total_size: int = Field(0, description="总大小（字节）")

    class Config:
        from_attributes = True


class DatasetDetailResponse(DatasetResponse):
    """数据集详情响应模式（包含文件列表）"""

    files: List[DataFileResponse] = Field(default_factory=list, description="文件列表")

    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    """数据集列表响应模式"""

    items: List[DatasetResponse]
    total: int
    skip: int
    limit: int


# ==================== 批量任务模式 ====================

class BatchJobCreate(BaseModel):
    """创建批量任务请求模式"""

    model_id: int = Field(..., description="使用的模型ID")
    confidence_threshold: float = Field(
        0.25, ge=0.0, le=1.0, description="置信度阈值"
    )
    iou_threshold: float = Field(
        0.45, ge=0.0, le=1.0, description="IOU阈值"
    )


class BatchJobResponse(BaseModel):
    """批量任务响应模式"""

    id: int
    dataset_id: int
    user_id: int
    model_id: int
    status: BatchJobStatus
    total_files: int
    completed_files: int
    failed_files: int
    confidence_threshold: Optional[str]
    iou_threshold: Optional[str]
    celery_group_id: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

    @property
    def progress_percentage(self) -> float:
        """计算进度百分比"""
        if self.total_files == 0:
            return 0.0
        return round((self.completed_files + self.failed_files) / self.total_files * 100, 2)


class BatchJobDetailResponse(BatchJobResponse):
    """批量任务详情响应模式（包含关联信息）"""

    dataset_name: Optional[str] = Field(None, description="数据集名称")
    model_name: Optional[str] = Field(None, description="模型名称")

    class Config:
        from_attributes = True


class BatchJobListResponse(BaseModel):
    """批量任务列表响应模式"""

    items: List[BatchJobDetailResponse]
    total: int
    skip: int
    limit: int


# ==================== 文件上传模式 ====================

class FileUploadResponse(BaseModel):
    """文件上传响应模式"""

    file_id: int
    filename: str
    file_size: int
    file_type: str
    message: str = "文件上传成功"


class BatchUploadResponse(BaseModel):
    """批量文件上传响应模式"""

    dataset_id: int
    uploaded_files: List[FileUploadResponse]
    total_uploaded: int
    total_size: int
    message: str = "批量上传成功"
