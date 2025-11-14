"""
数据集相关数据模型
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dataset(Base):
    """数据集模型"""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="数据集名称")
    description = Column(Text, nullable=True, comment="数据集描述")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建者ID")
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    # 关系
    files = relationship("DataFile", back_populates="dataset", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="dataset", cascade="all, delete-orphan")
    user = relationship("User", foreign_keys=[user_id])


class DataFile(Base):
    """数据文件模型"""

    __tablename__ = "data_files"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True, comment="所属数据集ID")
    filename = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    file_type = Column(String(20), nullable=False, comment="文件类型（image/video）")
    uploaded_at = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="上传时间")

    # 关系
    dataset = relationship("Dataset", back_populates="files")


class BatchJobStatus(str, enum.Enum):
    """批量任务状态"""

    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class BatchJob(Base):
    """批量检测任务模型"""

    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True, comment="数据集ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False, comment="使用的模型ID")

    status = Column(
        Enum(BatchJobStatus),
        default=BatchJobStatus.PENDING,
        nullable=False,
        index=True,
        comment="任务状态"
    )

    total_files = Column(Integer, nullable=False, default=0, comment="总文件数")
    completed_files = Column(Integer, nullable=False, default=0, comment="已完成文件数")
    failed_files = Column(Integer, nullable=False, default=0, comment="失败文件数")

    confidence_threshold = Column(String(10), nullable=True, comment="置信度阈值")
    iou_threshold = Column(String(10), nullable=True, comment="IOU阈值")

    celery_group_id = Column(String(255), nullable=True, comment="Celery Group任务ID")
    error_message = Column(Text, nullable=True, comment="错误信息")

    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="创建时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关系
    dataset = relationship("Dataset", back_populates="batch_jobs")
    user = relationship("User", foreign_keys=[user_id])
    model = relationship("MLModel", foreign_keys=[model_id])
