from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
import base64
from typing import Dict, Any, Optional

load_dotenv()

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

def analyze_image(image_data: str, description: str = "") -> str:
    """Analyze an image and provide description."""
    return f"Đây là một hình ảnh được tải lên. {description if description else 'Không có mô tả thêm.'}"

# Tạo model với streaming support
model = ChatOpenAI(
    model=os.getenv('MODEL'), 
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    streaming=True,  # Enable streaming
    temperature=0.7
)

# Tạo memory saver cho persistent memory
memory = MemorySaver()

# Tạo agent với streaming support và memory
agent = create_react_agent(
    model=model,
    tools=[get_weather, analyze_image],  
    checkpointer=memory,  # Thêm memory support
    prompt="""<default_system_instruction>
Bạn là một chuyên gia Kiểm thử phần mềm (QA/Test Engineer) có kinh nghiệm.  
Nhiệm vụ của bạn là chuyển đổi yêu cầu nghiệp vụ được cung cấp thành danh sách Testcase chi tiết.  


## Hướng dẫn chi tiết  
1. Đọc và phân tích yêu cầu nghiệp vụ.  
2. Sinh ra danh sách các Testcase đảm bảo bao phủ đầy đủ các luồng chính (happy case) và luồng phụ (negative case, exception) và yêu cầu non-function như bảo mật, hiệu năng 
3. Mỗi Testcase phải bao gồm các trường:  
   - title: mô tả ngắn gọn, dễ hiểu về mục tiêu kiểm thử.  
   - steps: danh sách các bước gồm:  
        - action: mô tả thao tác thực hiện.  
        - expected_result: kết quả mong đợi.  


## Yêu cầu chất lượng  
- Mỗi testcase phải ngắn gọn, rõ ràng, dễ thực hiện.  
- Bao phủ nhiều tình huống: dữ liệu hợp lệ, không hợp lệ, ngoại lệ.  
- Sử dụng ngôn ngữ chuẩn nghiệp vụ, không mơ hồ.  
</default_system_instruction>"""
)

class AgentManager:
    """Manager class để xử lý agent với thread_id và file attachments"""
    
    @staticmethod
    def create_message_with_context(
        title: str,
        pbi_requirement: str,
        file_content: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> str:
        """Tạo message với context đầy đủ cho agent"""
        
        message_parts = [
            f"**Tiêu đề:** {title}",
            f"**Yêu cầu PBI:** {pbi_requirement}"
        ]
        
        if file_content and file_name:
            message_parts.append(f"**File đính kèm:** {file_name}")
            message_parts.append(f"**Nội dung file:** {file_content[:1000]}..." if len(file_content) > 1000 else f"**Nội dung file:** {file_content}")
        
        return "\n\n".join(message_parts)