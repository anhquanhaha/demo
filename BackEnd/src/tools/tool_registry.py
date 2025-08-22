"""
Tool Registry for managing and organizing tools
"""
from typing import List, Dict, Any
from langchain_core.tools import BaseTool

from .basic_tools import get_current_time, calculator, get_weather


class ToolRegistry:
    """
    Registry để quản lý các tools của Agent
    Giúp dễ dàng thêm/xóa/quản lý tools
    """
    
    def __init__(self):
        self._tools = {}
        self._categories = {}
        self._init_default_tools()
    
    def _init_default_tools(self):
        """Khởi tạo các tools mặc định"""
        # Category: Utility tools
        self.register_tool("get_current_time", get_current_time, "utility")
        self.register_tool("calculator", calculator, "math") 
        self.register_tool("get_weather", get_weather, "information")
    
    def register_tool(self, name: str, tool: BaseTool, category: str = "general"):
        """
        Đăng ký một tool mới
        
        Args:
            name: Tên tool
            tool: Instance của tool
            category: Danh mục tool
        """
        self._tools[name] = tool
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
    
    def get_tool(self, name: str) -> BaseTool:
        """Lấy tool theo tên"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """Lấy tất cả tools"""
        return list(self._tools.values())
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Lấy tools theo category"""
        if category not in self._categories:
            return []
        
        return [self._tools[name] for name in self._categories[category]]
    
    def list_tools(self) -> Dict[str, Any]:
        """Liệt kê tất cả tools với thông tin"""
        result = {}
        for name, tool in self._tools.items():
            result[name] = {
                "description": tool.description,
                "category": self._get_tool_category(name)
            }
        return result
    
    def _get_tool_category(self, tool_name: str) -> str:
        """Tìm category của tool"""
        for category, tools in self._categories.items():
            if tool_name in tools:
                return category
        return "unknown"
    
    def remove_tool(self, name: str) -> bool:
        """Xóa tool"""
        if name in self._tools:
            # Xóa khỏi registry
            del self._tools[name]
            
            # Xóa khỏi category
            for category, tools in self._categories.items():
                if name in tools:
                    tools.remove(name)
                    break
                    
            return True
        return False
