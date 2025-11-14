"""
告警规则相关数据模型
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class AlertRule(Base):
    """告警规则模型"""

    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建者ID")
    name = Column(String(100), nullable=False, index=True, comment="规则名称")
    description = Column(Text, nullable=True, comment="规则描述")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用")

    # JSON字段存储条件和动作
    conditions = Column(JSON, nullable=False, comment="触发条件（JSON格式）")
    actions = Column(JSON, nullable=False, comment="执行动作（JSON格式）")

    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    # 关系
    logs = relationship("AlertLog", back_populates="rule", cascade="all, delete-orphan")
    user = relationship("User", foreign_keys=[user_id])


class AlertLogStatus(str, enum.Enum):
    """告警日志状态"""

    SUCCESS = "success"  # 成功执行
    FAILED = "failed"  # 执行失败
    PARTIAL = "partial"  # 部分成功


class AlertLog(Base):
    """告警日志模型"""

    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False, index=True, comment="告警规则ID")
    detection_id = Column(Integer, ForeignKey("detection_history.id"), nullable=False, index=True, comment="检测记录ID")

    triggered_at = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="触发时间")

    # JSON字段存储执行详情
    conditions_met = Column(JSON, nullable=False, comment="满足的条件（JSON格式）")
    actions_executed = Column(JSON, nullable=False, comment="执行的动作结果（JSON格式）")

    status = Column(String(20), default="success", nullable=False, index=True, comment="执行状态")

    # 关系
    rule = relationship("AlertRule", back_populates="logs")
    detection = relationship("DetectionHistory", foreign_keys=[detection_id])
