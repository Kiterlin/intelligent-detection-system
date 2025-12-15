"""
报告数据库模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReportStatus(str, Enum):
    """报告状态枚举"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """报告模型"""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False, comment="报告名称")
    report_type = Column(String(50), nullable=False, comment="报告类型: summary/detailed/comparison")
    status = Column(String(50), nullable=False, index=True, comment="状态: pending/generating/completed/failed")
    parameters_json = Column(JSON, nullable=True, comment="报告参数（时间范围、过滤条件等）")
    file_path_pdf = Column(String(500), nullable=True, comment="PDF文件路径")
    file_path_html = Column(String(500), nullable=True, comment="HTML文件路径")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关系
    user = relationship("User", backref="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', status='{self.status}')>"
