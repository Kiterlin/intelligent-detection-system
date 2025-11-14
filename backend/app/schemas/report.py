"""
报告相关的 Pydantic 模式
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# 报告参数模式
class ReportParameters(BaseModel):
    """报告参数"""

    time_range: Optional[Dict[str, Any]] = Field(None, description="时间范围 {start, end}")
    filters: Optional[Dict[str, Any]] = Field(None, description="过滤条件 {dataset_id, model_id, detection_type}")
    options: Optional[Dict[str, Any]] = Field(None, description="其他选项 {include_images, chart_style}")


# 报告创建请求
class ReportCreate(BaseModel):
    """报告创建请求"""

    name: str = Field(..., min_length=1, max_length=200, description="报告名称")
    report_type: str = Field(..., description="报告类型: summary/detailed/comparison")
    parameters: ReportParameters = Field(default_factory=ReportParameters, description="报告参数")


# 报告更新请求
class ReportUpdate(BaseModel):
    """报告更新请求"""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="报告名称")
    status: Optional[str] = Field(None, description="状态")


# 报告响应模式
class ReportResponse(BaseModel):
    """报告响应"""

    id: int = Field(..., description="报告ID")
    user_id: int = Field(..., description="用户ID")
    name: str = Field(..., description="报告名称")
    report_type: str = Field(..., description="报告类型")
    status: str = Field(..., description="状态")
    parameters_json: Optional[Dict[str, Any]] = Field(None, description="报告参数")
    file_path_pdf: Optional[str] = Field(None, description="PDF文件路径")
    file_path_html: Optional[str] = Field(None, description="HTML文件路径")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1


# 报告列表响应
class ReportListResponse(BaseModel):
    """报告列表响应"""

    total: int = Field(..., description="总数")
    reports: list[ReportResponse] = Field(..., description="报告列表")
