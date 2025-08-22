"""
FastAPI Application - Demo Project
"""
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional
import uvicorn
from Model import Item, ItemCreate, ChatMessage, ChatRequest, AgentTestcaseRequest, RequestCreate, RequestResponse, MessageResponse
from Service import ChatService
from database import db_manager

# Tạo instance FastAPI
app = FastAPI(
    title="Demo FastAPI Application",
    description="Ứng dụng FastAPI demo với các endpoints cơ bản",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Routes
@app.get("/")
async def root():
    """
    Endpoint chào mừng
    """
    return {
        "message": "Chào mừng đến với Demo FastAPI!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "Server đang hoạt động tốt"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint với streaming response
    """
    if request.stream:
        # Trả về streaming response
        return StreamingResponse(
            ChatService.generate_stream_response(request.messages),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    else:
        # Trả về response thông thường (non-streaming)
        try:
            return await ChatService.process_chat_request(request.messages)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-testcase")
async def agent_testcase(
    conversation_id: Optional[str] = Form(None),
    title: str = Form(...),
    pbi_requirement: str = Form(...),
    file_attachment: Optional[UploadFile] = File(None)
):
    """
    Agent testcase endpoint với streaming response
    
    Args:
        conversation_id: Thread ID cho memory persistence (optional)
        title: Tiêu đề của testcase
        pbi_requirement: Yêu cầu PBI
        file_attachment: File đính kèm (optional)
    
    Returns:
        StreamingResponse: Server-Sent Events stream
    """
    try:
        # Trả về streaming response
        return StreamingResponse(
            ChatService.process_agent_testcase_stream(
                conversation_id=conversation_id,
                title=title,
                pbi_requirement=pbi_requirement,
                file_attachment=file_attachment
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý agent testcase: {str(e)}")

# Request Management APIs
@app.post("/requests", response_model=RequestResponse)
async def create_request(request: RequestCreate):
    """Tạo request mới"""
    try:
        result = db_manager.create_request(request.title, request.pbi_requirement)
        if result:
            return RequestResponse(**result)
        else:
            raise HTTPException(status_code=500, detail="Không thể tạo request")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests", response_model=List[RequestResponse])
async def get_all_requests():
    """Lấy tất cả requests"""
    try:
        requests = db_manager.get_all_requests()
        return [RequestResponse(**req) for req in requests]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests/{conversation_id}", response_model=RequestResponse)
async def get_request(conversation_id: str):
    """Lấy request theo conversation_id"""
    try:
        request = db_manager.get_request_by_conversation_id(conversation_id)
        if request:
            return RequestResponse(**request)
        else:
            raise HTTPException(status_code=404, detail="Request không tồn tại")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: str):
    """Lấy tất cả messages của một conversation"""
    try:
        messages = db_manager.get_messages_by_conversation_id(conversation_id)
        return [MessageResponse(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/requests/{conversation_id}")
async def delete_request(conversation_id: str):
    """Xóa request và tất cả messages liên quan"""
    try:
        success = db_manager.delete_request(conversation_id)
        if success:
            return {"message": "Request đã được xóa thành công"}
        else:
            raise HTTPException(status_code=404, detail="Request không tồn tại")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chạy server nếu file được execute trực tiếp
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
