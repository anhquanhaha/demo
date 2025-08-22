"""
Service layer cho Test Cases
"""

from typing import List, Optional, Dict, Any
from database import db_manager
from Model.testcase_models import (
    TestCaseCreate, 
    TestCaseUpdate, 
    TestCaseResponse, 
    TestCaseListResponse,
    TestCaseSearchRequest
)

class TestCaseService:
    """Service class để xử lý business logic cho test cases"""
    
    def __init__(self):
        self.db = db_manager
    
    def create_test_case(self, test_case_data: TestCaseCreate, conversation_id: str = "default") -> Optional[TestCaseResponse]:
        """Tạo test case mới"""
        try:
            result = self.db.create_test_case(
                conversation_id=conversation_id,
                title=test_case_data.title,
                steps=test_case_data.steps
            )
            
            if result:
                return TestCaseResponse(**result)
            return None
            
        except Exception as e:
            print(f"Error creating test case: {e}")
            return None
    
    def get_all_test_cases(self) -> TestCaseListResponse:
        """Lấy tất cả test cases"""
        try:
            results = self.db.get_all_test_cases()
            test_cases = [TestCaseResponse(**result) for result in results]
            
            return TestCaseListResponse(
                test_cases=test_cases,
                total=len(test_cases)
            )
            
        except Exception as e:
            print(f"Error getting all test cases: {e}")
            return TestCaseListResponse(test_cases=[], total=0)
    
    def get_test_case_by_id(self, test_case_id: int) -> Optional[TestCaseResponse]:
        """Lấy test case theo ID"""
        try:
            result = self.db.get_test_case_by_id(test_case_id)
            
            if result:
                return TestCaseResponse(**result)
            return None
            
        except Exception as e:
            print(f"Error getting test case by id: {e}")
            return None
    
    def update_test_case(self, test_case_id: int, update_data: TestCaseUpdate) -> Optional[TestCaseResponse]:
        """Cập nhật test case"""
        try:
            # Chỉ update các field có giá trị
            success = self.db.update_test_case(
                test_case_id=test_case_id,
                title=update_data.title,
                steps=update_data.steps
            )
            
            if success:
                # Lấy test case đã được update
                return self.get_test_case_by_id(test_case_id)
            return None
            
        except Exception as e:
            print(f"Error updating test case: {e}")
            return None
    
    def delete_test_case(self, test_case_id: int) -> bool:
        """Xóa test case"""
        try:
            return self.db.delete_test_case(test_case_id)
            
        except Exception as e:
            print(f"Error deleting test case: {e}")
            return False
    
    def search_test_cases(self, search_request: TestCaseSearchRequest) -> TestCaseListResponse:
        """Tìm kiếm test cases"""
        try:
            results = self.db.search_test_cases(search_request.keyword)
            test_cases = [TestCaseResponse(**result) for result in results]
            
            return TestCaseListResponse(
                test_cases=test_cases,
                total=len(test_cases)
            )
            
        except Exception as e:
            print(f"Error searching test cases: {e}")
            return TestCaseListResponse(test_cases=[], total=0)
    
    def get_test_cases_by_title_pattern(self, pattern: str) -> TestCaseListResponse:
        """Lấy test cases theo pattern title"""
        try:
            results = self.db.search_test_cases(pattern)
            # Lọc chỉ những test case có title match pattern
            filtered_results = [
                result for result in results 
                if pattern.lower() in result['title'].lower()
            ]
            
            test_cases = [TestCaseResponse(**result) for result in filtered_results]
            
            return TestCaseListResponse(
                test_cases=test_cases,
                total=len(test_cases)
            )
            
        except Exception as e:
            print(f"Error getting test cases by title pattern: {e}")
            return TestCaseListResponse(test_cases=[], total=0)
    
    def create_multiple_test_cases(self, testcase_titles: List[str], testcase_steps: List[str], conversation_id: str = "default") -> List[Optional[TestCaseResponse]]:
        """Tạo nhiều test cases cùng lúc"""
        created_test_cases = []
        
        try:
            # Đảm bảo số lượng titles và steps khớp nhau
            min_length = min(len(testcase_titles), len(testcase_steps))
            
            for i in range(min_length):
                test_case_data = TestCaseCreate(
                    title=testcase_titles[i],
                    steps=testcase_steps[i]
                )
                
                created_test_case = self.create_test_case(test_case_data, conversation_id)
                created_test_cases.append(created_test_case)
                
        except Exception as e:
            print(f"Error creating multiple test cases: {e}")
            
        return created_test_cases

# Singleton instance
testcase_service = TestCaseService()
