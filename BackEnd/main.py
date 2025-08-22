"""
FastAPI Application - Demo Project
"""
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional
import uvicorn
import base64
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
        # Preload nội dung file (nếu có) để tránh lỗi stream bị đóng khi streaming response
        preloaded_file_name = None
        preloaded_file_content = None
        preloaded_base64_data = None
        preloaded_mime_type = None
        
        if file_attachment is not None:
            try:
                try:
                    await file_attachment.seek(0)
                except Exception:
                    pass
                file_bytes = await file_attachment.read()
                preloaded_file_name = file_attachment.filename or "unknown_file"
                
                if not file_bytes or len(file_bytes) == 0:
                    preloaded_file_content = f"[EMPTY FILE: {preloaded_file_name}]"
                else:
                    if file_attachment.content_type and file_attachment.content_type.startswith('image/'):
                        # Cho file ảnh: tạo base64 data và content description
                        preloaded_base64_data = base64.b64encode(file_bytes).decode('utf-8')
                        preloaded_mime_type = file_attachment.content_type
                        preloaded_file_content = f"[IMAGE: {preloaded_file_name}] - Size: {len(file_bytes)} bytes, Content-Type: {file_attachment.content_type}"
                    else:
                        # Cho file text: decode nội dung
                        try:
                            text_content = file_bytes.decode('utf-8')
                            if len(text_content) > 2000:
                                text_content = text_content[:2000] + "... (truncated)"
                            preloaded_file_content = text_content
                        except UnicodeDecodeError:
                            try:
                                text_content = file_bytes.decode('latin-1')
                                if len(text_content) > 2000:
                                    text_content = text_content[:2000] + "... (truncated)"
                                preloaded_file_content = text_content
                            except Exception:
                                preloaded_file_content = f"[BINARY FILE: {preloaded_file_name}] - Size: {len(file_bytes)} bytes"
            except Exception as preload_err:
                preloaded_file_name = file_attachment.filename or "unknown_file"
                preloaded_file_content = f"[ERROR READING FILE: {preloaded_file_name}] - {str(preload_err)}"

        # Trả về streaming response với nội dung file đã preload
        return StreamingResponse(
            ChatService.process_agent_testcase_stream(
                conversation_id=conversation_id,
                title=title,
                pbi_requirement=pbi_requirement,
                file_attachment=None,
                preloaded_file_name=preloaded_file_name,
                preloaded_file_content=preloaded_file_content,
                preloaded_base64_data=preloaded_base64_data,
                preloaded_mime_type=preloaded_mime_type
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

@app.put("/agent-testcase")
async def agent_testcase_edit(
    conversation_id: str = Form(...),
    prompt: str = Form(...),
    file_attachment: Optional[UploadFile] = File(None)
):
    """
    Agent testcase edit endpoint với streaming response và file attachment
    
    Args:
        conversation_id: Thread ID của conversation cần edit (required)
        prompt: Yêu cầu chỉnh sửa từ người dùng (required)
        file_attachment: File đính kèm (optional)
    
    Returns:
        StreamingResponse: Server-Sent Events stream
    """
    try:
        # Kiểm tra conversation_id có tồn tại không
        request = db_manager.get_request_by_conversation_id(conversation_id)
        if not request:
            raise HTTPException(status_code=404, detail="Conversation không tồn tại")
        
        # Preload file content (nếu có) để tránh lỗi stream bị đóng
        preloaded_file_name = None
        preloaded_file_content = None
        preloaded_base64_data = None
        preloaded_mime_type = None
        
        if file_attachment is not None:
            try:
                try:
                    await file_attachment.seek(0)
                except Exception:
                    pass
                file_bytes = await file_attachment.read()
                preloaded_file_name = file_attachment.filename or "unknown_file"
                
                if not file_bytes or len(file_bytes) == 0:
                    preloaded_file_content = f"[EMPTY FILE: {preloaded_file_name}]"
                else:
                    if file_attachment.content_type and file_attachment.content_type.startswith('image/'):
                        # Cho file ảnh: tạo base64 data và content description
                        preloaded_base64_data = base64.b64encode(file_bytes).decode('utf-8')
                        preloaded_mime_type = file_attachment.content_type
                        preloaded_file_content = f"[IMAGE: {preloaded_file_name}] - Size: {len(file_bytes)} bytes, Content-Type: {file_attachment.content_type}"
                    else:
                        # Cho file text: decode nội dung
                        try:
                            text_content = file_bytes.decode('utf-8')
                            if len(text_content) > 2000:
                                text_content = text_content[:2000] + "... (truncated)"
                            preloaded_file_content = text_content
                        except UnicodeDecodeError:
                            try:
                                text_content = file_bytes.decode('latin-1')
                                if len(text_content) > 2000:
                                    text_content = text_content[:2000] + "... (truncated)"
                                preloaded_file_content = text_content
                            except Exception:
                                preloaded_file_content = f"[BINARY FILE: {preloaded_file_name}] - Size: {len(file_bytes)} bytes"
            except Exception as preload_err:
                preloaded_file_name = file_attachment.filename or "unknown_file"
                preloaded_file_content = f"[ERROR READING FILE: {preloaded_file_name}] - {str(preload_err)}"
        
        # Trả về streaming response với file support
        return StreamingResponse(
            ChatService.process_agent_testcase_edit_stream(
                conversation_id=conversation_id,
                prompt=prompt,
                file_attachment=None,
                preloaded_file_name=preloaded_file_name,
                preloaded_file_content=preloaded_file_content,
                preloaded_base64_data=preloaded_base64_data,
                preloaded_mime_type=preloaded_mime_type
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý agent testcase edit: {str(e)}")


# Chạy server nếu file được execute trực tiếp
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
