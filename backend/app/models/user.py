"""
用户数据库模型
"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum as SQLEnum
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
