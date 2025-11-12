"""
机器学习模型相关的 Pydantic 模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.ml_model import ModelStatus


# 模型上传模式
class ModelUpload(BaseModel):
    """模型上传请求模式"""

    name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    version: Optional[str] = Field(None, max_length=50, description="模型版本")
    description: Optional[str] = Field(None, description="模型描述")


# 模型更新模式
class ModelUpdate(BaseModel):
    """模型更新请求模式"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模型名称")
    version: Optional[str] = Field(None, max_length=50, description="模型版本")
    description: Optional[str] = Field(None, description="模型描述")


# 模型状态更新模式
class ModelStatusUpdate(BaseModel):
    """模型状态更新请求模式"""

    status: ModelStatus = Field(..., description="模型状态")


# 模型响应模式
class ModelResponse(BaseModel):
    """模型响应模式"""

    id: int
    name: str
    filename: str
    file_path: str
    version: Optional[str]
    status: ModelStatus
    description: Optional[str]
    file_size: Optional[int]
    uploaded_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 支持从 ORM 模型创建


# 模型列表响应模式
class ModelListResponse(BaseModel):
    """模型列表响应模式"""

    models: list[ModelResponse]
    total: int
    page: int
    page_size: int
