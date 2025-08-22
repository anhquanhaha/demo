"""
Pydantic models cho Chat-related endpoints
"""

from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

class ChatMessage(BaseModel):
    """Model cho một tin nhắn trong cuộc trò chuyện"""
    role: str  # "user" hoặc "assistant"
    content: str
    
    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "Xin chào! Bạn có thể giúp tôi không?"
            }
        }

class ChatRequest(BaseModel):
    """Model cho request tới chat endpoint"""
    messages: List[ChatMessage]
    stream: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Xin chào! Bạn có thể giúp tôi không?"
                    }
                ],
                "stream": True
            }
        }

class AgentTestcaseRequest(BaseModel):
    """Model cho request tới agent-testcase endpoint"""
    conversation_id: Optional[str] = None  # thread_id của agent
    title: str
    pbi_requirement: str
    # file_attachment sẽ được handle riêng qua Form data
    
    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "thread_123",
                "title": "Màn hình đăng nhập",
                "pbi_requirement": "Yêu cầu của màn hình đăng nhập"
            }
        }
