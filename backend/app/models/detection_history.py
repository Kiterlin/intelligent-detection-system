"""
检测历史数据库模型
"""
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Enum as SQLEnum,
    ForeignKey,
    Text,
    Float,
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DetectionInputType(str, enum.Enum):
    """检测输入类型枚举"""

    IMAGE = "image"
    VIDEO = "video"


class DetectionStatus(str, enum.Enum):
    """检测状态枚举"""

    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class DetectionHistory(Base):
    """检测历史记录模型"""

    __tablename__ = "detection_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID"
    )
    model_id = Column(
        Integer,
        ForeignKey("ml_models.id"),
        nullable=False,
        index=True,
        comment="使用的模型ID",
    )

    # 输入输出信息
    input_type = Column(
        SQLEnum(DetectionInputType), nullable=False, comment="输入类型（图片/视频）"
    )
    input_file_path = Column(String(500), nullable=False, comment="输入文件路径")
    output_file_path = Column(String(500), nullable=True, comment="输出文件路径")

    # 检测结果
    result_json = Column(Text, nullable=True, comment="检测结果JSON")
    detected_objects_count = Column(Integer, default=0, comment="检测到的对象数量")

    # 任务状态
    status = Column(
        SQLEnum(DetectionStatus),
        default=DetectionStatus.PENDING,
        nullable=False,
        index=True,
        comment="检测状态",
    )
    task_id = Column(String(100), nullable=True, index=True, comment="Celery任务ID")

    # 性能指标
    processing_time = Column(Float, nullable=True, comment="处理时间（秒）")

    # 检测参数
    confidence_threshold = Column(Float, nullable=True, comment="置信度阈值")
    iou_threshold = Column(Float, nullable=True, comment="IOU阈值")

    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间",
    )

    # 关系
    user = relationship("User", foreign_keys=[user_id])
    model = relationship("MLModel", foreign_keys=[model_id])

    def __repr__(self):
        return f"<DetectionHistory(id={self.id}, user_id={self.user_id}, type='{self.input_type}', status='{self.status}')>"
