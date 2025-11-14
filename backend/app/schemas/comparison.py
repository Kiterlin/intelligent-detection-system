"""
检测结果对比相关的 Pydantic 模式
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# 匹配的对象对
class MatchedObjectPair(BaseModel):
    """匹配的对象对"""

    first: Dict[str, Any] = Field(..., description="第一个检测对象")
    second: Dict[str, Any] = Field(..., description="第二个检测对象")
    iou: float = Field(..., description="IOU值")
    class_match: bool = Field(..., description="类别是否匹配")


# 匹配统计
class MatchStats(BaseModel):
    """匹配统计信息"""

    total_in_first: int = Field(..., description="第一个结果的对象总数")
    total_in_second: int = Field(..., description="第二个结果的对象总数")
    common_count: int = Field(..., description="共同对象数量")
    unique_to_first_count: int = Field(..., description="仅在第一个结果中的对象数量")
    unique_to_second_count: int = Field(..., description="仅在第二个结果中的对象数量")
    match_rate: float = Field(..., description="匹配率（百分比）")


# 对比分析结果
class ComparisonAnalysis(BaseModel):
    """对比分析结果"""

    common_objects: List[MatchedObjectPair] = Field(..., description="共同对象列表")
    unique_to_first: List[Dict[str, Any]] = Field(..., description="仅在第一个结果中的对象")
    unique_to_second: List[Dict[str, Any]] = Field(..., description="仅在第二个结果中的对象")
    match_stats: MatchStats = Field(..., description="匹配统计")


# 检测记录元数据
class DetectionRecordMetadata(BaseModel):
    """检测记录元数据"""

    detection_id: int = Field(..., description="检测记录ID")
    count: int = Field(..., description="检测对象数量")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


# 统计对比 - 单个指标
class StatMetric(BaseModel):
    """单个统计指标对比"""

    first: float = Field(..., description="第一个结果的值")
    second: float = Field(..., description="第二个结果的值")
    diff: float = Field(..., description="差异值")


# 模型对比
class ModelComparison(BaseModel):
    """模型对比"""

    first: Optional[int] = Field(None, description="第一个使用的模型ID")
    second: Optional[int] = Field(None, description="第二个使用的模型ID")
    same: bool = Field(..., description="是否使用相同模型")


# 参数对比
class ParameterComparison(BaseModel):
    """参数对比"""

    first: Optional[float] = Field(None, description="第一个结果的参数值")
    second: Optional[float] = Field(None, description="第二个结果的参数值")


# 统计对比结果
class StatisticsComparison(BaseModel):
    """统计对比结果"""

    detection_count: StatMetric = Field(..., description="检测对象数量对比")
    processing_time: StatMetric = Field(..., description="处理时间对比")
    model: ModelComparison = Field(..., description="模型对比")
    parameters: Dict[str, ParameterComparison] = Field(..., description="参数对比")


# 完整对比响应
class ComparisonResponse(BaseModel):
    """检测结果对比响应"""

    records: List[DetectionRecordMetadata] = Field(..., description="参与对比的检测记录")
    comparison: ComparisonAnalysis = Field(..., description="对比分析结果")
    statistics: Optional[StatisticsComparison] = Field(None, description="统计对比结果")
