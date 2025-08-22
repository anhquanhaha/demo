"""
Models cho Test Cases
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TestCaseCreate(BaseModel):
    """Model để tạo test case mới"""
    title: str = Field(..., min_length=1, max_length=200, description="Tiêu đề test case")
    steps: str = Field(..., min_length=1, description="Các bước thực hiện test case")

class TestCaseUpdate(BaseModel):
    """Model để cập nhật test case"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Tiêu đề test case")
    steps: Optional[str] = Field(None, min_length=1, description="Các bước thực hiện test case")

class TestCaseResponse(BaseModel):
    """Model response cho test case"""
    id: int
    title: str
    steps: str
    created_at: str
    updated_at: str

class TestCaseListResponse(BaseModel):
    """Model response cho danh sách test cases"""
    test_cases: list[TestCaseResponse]
    total: int

class TestCaseSearchRequest(BaseModel):
    """Model để tìm kiếm test cases"""
    keyword: str = Field(..., min_length=1, description="Từ khóa tìm kiếm")
    