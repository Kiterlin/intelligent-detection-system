"""
训练任务模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class TrainingJob(Base):
    """训练任务模型"""
    __tablename__ = "training_jobs"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 关联字段
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    base_model_id = Column(Integer, ForeignKey("ml_models.id", ondelete="RESTRICT"), nullable=False)
    new_model_id = Column(Integer, ForeignKey("ml_models.id", ondelete="SET NULL"), nullable=True)

    # 基本信息
    job_name = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default='pending', index=True)
    # 状态: 'pending', 'preparing', 'training', 'completed', 'failed', 'cancelled'

    # 训练配置 (JSON)
    config_json = Column(JSON, nullable=False)
    dataset_config = Column(JSON, nullable=True)

    # 输出文件路径
    log_file_path = Column(String(500), nullable=True)
    weights_path = Column(String(500), nullable=True)
    results_path = Column(String(500), nullable=True)

    # 性能指标 (JSON)
    metrics_json = Column(JSON, nullable=True)

    # 进度跟踪
    current_epoch = Column(Integer, nullable=True, default=0)
    total_epochs = Column(Integer, nullable=True)
    progress_percentage = Column(Float, nullable=True, default=0.0)

    # 错误信息
    error_message = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 关系
    admin = relationship("User", foreign_keys=[admin_id])
    base_model = relationship("MLModel", foreign_keys=[base_model_id])
    new_model = relationship("MLModel", foreign_keys=[new_model_id])

    def __repr__(self):
        return f"<TrainingJob(id={self.id}, name='{self.job_name}', status='{self.status}')>"
