"""
Token 相关的 Pydantic 模式
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token 响应模式"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据模式"""

    username: Optional[str] = None
    user_id: Optional[int] = None
