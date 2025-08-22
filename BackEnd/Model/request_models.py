"""
Pydantic models cho Request management
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RequestCreate(BaseModel):
    """Model để tạo request mới"""
    title: str
    pbi_requirement: str
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Màn hình đăng nhập",
                "pbi_requirement": "Yêu cầu của màn hình đăng nhập..."
            }
        }

class RequestResponse(BaseModel):
    """Model cho response của request"""
    id: int
    conversation_id: str
    title: str
    pbi_requirement: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": "conv_123456",
                "title": "Màn hình đăng nhập",
                "pbi_requirement": "Yêu cầu của màn hình đăng nhập...",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }

class MessageResponse(BaseModel):
    """Model cho response của message"""
    id: int
    conversation_id: str
    role: str  # "user" hoặc "assistant"
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": "conv_123456",
                "role": "user",
                "content": "Phân tích yêu cầu này...",
                "created_at": "2024-01-01T00:00:00"
            }
        }
