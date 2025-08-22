import asyncio
from datetime import datetime
from typing import Literal, Optional

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from typing import List, Dict, Any  
from Service.testcase_service import testcase_service




class SaveTestcaseInputs(BaseModel):
    testcase_titles: List[str] = Field(
        description="Danh sách tiêu đề của test case: mô tả tóm tắt nội dung testcase"
    )
    testcase_steps: List[str] = Field(
        description="Danh sách các bước thực hiện bao gồm từng bước thực hiện testcase và kết quả mong muốn"
    )


@tool(args_schema=SaveTestcaseInputs)
def save_testcase(
    testcase_titles: List[str],
    testcase_steps: List[str],
    config: RunnableConfig,
) -> dict:
    """
    Bắt buộc sử dụng tool này để phản hổi người dùng danh sách testcase sinh ra.

    Args:
        testcase_titles: List[str]
            Danh sách tiêu đề của test case: mô tả tóm tắt nội dung testcase
        testcase_steps: Danh sách các bước thực hiện bao gồm từng bước thực hiện testcase và kết quả mong muốn
            ví dụ:
            "1. Step1
                action: Mô tả thao tác,
                expected_result: Kết quả mong đợi
            2. Step2
                action: Mô tả thao tác tiếp theo,
                expected_result: Kết quả mong đợi"

    Returns:
        dict: Kết quả của việc phản hồi thông tin người dùng
    """
    try:
        # Get user context from config
        conversation_id = config.get("thread_id", f"conv_defaut")
        
        print(f"Saving {len(testcase_titles)} test cases to database...")
        print(f"Titles: {testcase_titles}")
        print(f"Steps: {testcase_steps}")
        
        # Validate input
        if not testcase_titles or not testcase_steps:
            return {
                "success": False,
                "message": "Danh sách testcase không được để trống",
                "error": "Empty testcase lists"
            }
        
        if len(testcase_titles) != len(testcase_steps):
            return {
                "success": False,
                "message": f"Số lượng tiêu đề ({len(testcase_titles)}) không khớp với số lượng bước thực hiện ({len(testcase_steps)})",
                "error": "Mismatched titles and steps count"
            }
        
        # Save test cases to database
        created_test_cases = testcase_service.create_multiple_test_cases(
            testcase_titles=testcase_titles,
            testcase_steps=testcase_steps,
            conversation_id=conversation_id
        )
        
        # Count successful saves
        successful_saves = len([tc for tc in created_test_cases if tc is not None])
        
        if successful_saves == 0:
            return {
                "success": False,
                "message": "Không thể lưu testcase nào vào database",
                "error": "No test cases saved"
            }
        elif successful_saves < len(testcase_titles):
            return {
                "success": True,
                "message": f"Đã lưu {successful_saves}/{len(testcase_titles)} testcases vào database",
                "data": {
                    "saved_count": successful_saves,
                    "total_count": len(testcase_titles),
                    "conversation_id": conversation_id
                }
            }
        else:
            return {
                "success": True,
                "message": f"Đã lưu thành công {successful_saves} testcases vào database",
                "data": {
                    "saved_count": successful_saves,
                    "total_count": len(testcase_titles),
                    "conversation_id": conversation_id
                }
            }

    except Exception as e:
        print(f"Error in save_testcase: {str(e)}")
        return {
            "success": False,
            "message": f"Lỗi khi lưu testcase: {str(e)}",
            "error": str(e),
        }
