"""
Pydantic models cho Item-related endpoints
"""

from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    """Model cho Item entity"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemCreate(BaseModel):
    """Model cho việc tạo Item mới"""
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
