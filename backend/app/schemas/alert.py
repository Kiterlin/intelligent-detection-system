"""
告警规则相关的 Pydantic 模式
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ==================== 条件和动作模式 ====================

class AlertConditions(BaseModel):
    """告警触发条件模式"""

    target_classes: List[str] = Field(
        default_factory=list,
        description="目标类别列表（例如：['fish', 'shark']）"
    )
    min_count: int = Field(1, ge=1, description="最小目标数量")
    min_confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="最小置信度阈值"
    )
    dataset_id: Optional[int] = Field(None, description="特定数据集ID（可选）")


class EmailAction(BaseModel):
    """邮件通知动作"""

    enabled: bool = Field(False, description="是否启用邮件通知")
    recipients: List[str] = Field(
        default_factory=list, description="收件人邮箱列表"
    )


class WebhookAction(BaseModel):
    """Webhook通知动作"""

    enabled: bool = Field(False, description="是否启用Webhook通知")
    url: str = Field("", description="Webhook URL")
    method: str = Field("POST", description="HTTP方法")


class AlertActions(BaseModel):
    """告警执行动作模式"""

    email: EmailAction = Field(
        default_factory=EmailAction, description="邮件通知配置"
    )
    webhook: WebhookAction = Field(
        default_factory=WebhookAction, description="Webhook通知配置"
    )


# ==================== 告警规则模式 ====================

class AlertRuleBase(BaseModel):
    """告警规则基础模式"""

    name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    is_active: bool = Field(True, description="是否启用")


class AlertRuleCreate(AlertRuleBase):
    """创建告警规则请求模式"""

    conditions: Dict[str, Any] = Field(..., description="触发条件（JSON格式）")
    actions: Dict[str, Any] = Field(..., description="执行动作（JSON格式）")


class AlertRuleUpdate(BaseModel):
    """更新告警规则请求模式"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    conditions: Optional[Dict[str, Any]] = Field(None, description="触发条件（JSON格式）")
    actions: Optional[Dict[str, Any]] = Field(None, description="执行动作（JSON格式）")
    is_active: Optional[bool] = Field(None, description="是否启用")


class AlertRuleResponse(BaseModel):
    """告警规则响应模式"""

    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_active: bool
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    # 统计信息（可通过关联计算）
    trigger_count: int = Field(0, description="触发次数")

    class Config:
        from_attributes = True


class AlertRuleToggle(BaseModel):
    """切换告警规则启用状态请求模式"""

    is_active: bool = Field(..., description="是否启用")


class AlertRuleListResponse(BaseModel):
    """告警规则列表响应模式"""

    items: List[AlertRuleResponse]
    total: int
    skip: int
    limit: int


# ==================== 告警日志模式 ====================

class AlertLogResponse(BaseModel):
    """告警日志响应模式"""

    id: int
    rule_id: int
    detection_id: int
    triggered_at: datetime
    conditions_met: Dict[str, Any]
    actions_executed: Dict[str, Any]
    status: str

    # 关联信息
    rule_name: Optional[str] = Field(None, description="规则名称")
    detection_type: Optional[str] = Field(None, description="检测类型")

    class Config:
        from_attributes = True


class AlertLogListResponse(BaseModel):
    """告警日志列表响应模式"""

    items: List[AlertLogResponse]
    total: int
    skip: int
    limit: int


# ==================== 告警统计模式 ====================

class AlertStats(BaseModel):
    """告警统计信息模式"""

    total_rules: int = Field(0, description="总规则数")
    active_rules: int = Field(0, description="启用规则数")
    total_triggers: int = Field(0, description="总触发次数")
    success_rate: float = Field(0.0, description="成功率")
