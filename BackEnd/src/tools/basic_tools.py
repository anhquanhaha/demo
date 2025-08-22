"""
Basic tools for AI Agent
"""
from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Lấy thời gian hiện tại.
    
    Returns:
        str: Thời gian hiện tại theo định dạng YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculator(expression: str) -> str:
    """Tính toán biểu thức toán học đơn giản một cách an toàn.
    
    Args:
        expression (str): Biểu thức toán học (ví dụ: "2 + 3 * 4")
        
    Returns:
        str: Kết quả tính toán hoặc thông báo lỗi
        
    Examples:
        >>> calculator("2 + 3 * 4")
        "Kết quả: 14"
        >>> calculator("10 / 2")
        "Kết quả: 5.0"
    """
    try:
        # Chỉ cho phép các ký tự an toàn
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Lỗi: Chỉ cho phép các ký tự số và phép toán cơ bản (+, -, *, /, (), .)"
        
        # Kiểm tra các từ khóa nguy hiểm
        dangerous_keywords = ['import', '__', 'exec', 'eval', 'open', 'file']
        if any(keyword in expression.lower() for keyword in dangerous_keywords):
            return "Lỗi: Biểu thức chứa từ khóa không được phép"
        
        result = eval(expression)
        return f"Kết quả: {result}"
        
    except ZeroDivisionError:
        return "Lỗi: Không thể chia cho 0"
    except SyntaxError:
        return "Lỗi: Cú pháp biểu thức không hợp lệ"
    except Exception as e:
        return f"Lỗi tính toán: {str(e)}"


@tool
def get_weather(location: str) -> str:
    """Lấy thông tin thời tiết cho địa điểm được chỉ định.
    
    Args:
        location (str): Tên địa điểm cần xem thời tiết
        
    Returns:
        str: Thông tin thời tiết hoặc thông báo không tìm thấy
        
    Note:
        Hiện tại sử dụng mock data. Trong production có thể tích hợp API thật.
        
    Examples:
        >>> get_weather("Hà Nội")
        "Hà Nội: 25°C, trời nắng"
    """
    # Mock data - có thể thay thế bằng API thời tiết thật
    mock_weather_data = {
        "hanoi": "Hà Nội: 25°C, trời nắng ☀️",
        "saigon": "TP.HCM: 28°C, có mây ⛅",
        "danang": "Đà Nẵng: 26°C, trời mưa nhẹ 🌦️",
        "hochiminh": "TP.HCM: 28°C, có mây ⛅",
        "hcm": "TP.HCM: 28°C, có mây ⛅"
    }
    
    # Chuẩn hóa tên địa điểm
    location_normalized = location.lower().strip()
    
    # Tìm kiếm thông tin thời tiết
    for city_key, weather_info in mock_weather_data.items():
        if city_key in location_normalized or location_normalized in city_key:
            return weather_info
    
    return f"❌ Không tìm thấy thông tin thời tiết cho '{location}'. Hiện tại chỉ hỗ trợ: Hà Nội, TP.HCM, Đà Nẵng"
