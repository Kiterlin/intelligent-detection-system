"""
机器学习模型数据库模型
"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ModelStatus(str, enum.Enum):
    """模型状态枚举"""

    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 停用


class MLModel(Base):
    """机器学习模型"""

    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="模型名称")
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, unique=True, comment="文件存储路径")
    version = Column(String(50), nullable=True, comment="模型版本")
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.INACTIVE, nullable=False, comment="模型状态")
    description = Column(Text, nullable=True, comment="模型描述")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上传者ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间"
    )

    # 关系：上传者
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<MLModel(id={self.id}, name='{self.name}', status='{self.status}')>"
