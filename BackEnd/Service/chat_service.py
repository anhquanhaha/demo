"""
Chat Service - Xử lý logic chat và streaming
"""
from typing import List, AsyncGenerator, Dict, Any, Optional
import json
import base64
import asyncio
import time
from Model import ChatMessage
from agent import agent, AgentManager
from fastapi import UploadFile
from database import db_manager


class ChatService:
    """
    Service class để xử lý các chức năng chat
    """
    
    @staticmethod
    async def generate_stream_response(messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """
        Generator function để tạo streaming response từ agent
        
        Args:
            messages: Danh sách các tin nhắn chat
            
        Yields:
            str: Server-Sent Events formatted strings
        """
        try:
            # Convert ChatMessage objects to dict format for agent
            agent_messages = []
            for msg in messages:
                agent_messages.append({
                    "role": msg.role, 
                    "content": msg.content
                })
            
            # Gọi agent với streaming
            response = agent.astream({"messages": agent_messages})
            
            # Stream từng chunk của response
            async for chunk in response:
                # Langgraph agent trả về structure: {'agent': {'messages': [...]}}
                if isinstance(chunk, dict):
                    # Kiểm tra structure của langgraph
                    if 'agent' in chunk and isinstance(chunk['agent'], dict):
                        agent_data = chunk['agent']
                        if 'messages' in agent_data:
                            for message in agent_data['messages']:
                                if hasattr(message, 'content') and message.content:
                                    # Split content thành chunks nhỏ để tạo streaming effect
                                    content = message.content
                                    chunk_size = 50  # Chia nhỏ content
                                    
                                    for i in range(0, len(content), chunk_size):
                                        chunk_content = content[i:i + chunk_size]
                                        data = {
                                            "type": "chunk",
                                            "content": chunk_content,
                                            "role": "assistant"
                                        }
                                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                                        
                                        # Thêm delay nhỏ để tạo streaming effect
                                        await asyncio.sleep(0.05)
                    
                    # Fallback cho structure cũ
                    elif 'messages' in chunk:
                        for message in chunk['messages']:
                            if hasattr(message, 'content') and message.content:
                                data = {
                                    "type": "message",
                                    "content": message.content,
                                    "role": "assistant"
                                }
                                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # Gửi signal kết thúc stream
            yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            # Gửi lỗi qua stream
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    @staticmethod
    async def process_chat_request(messages: List[ChatMessage]) -> Dict[str, Any]:
        """
        Xử lý chat request không streaming
        
        Args:
            messages: Danh sách các tin nhắn chat
            
        Returns:
            Dict: Response data với role và content
            
        Raises:
            Exception: Nếu có lỗi trong quá trình xử lý
        """
        try:
            # Convert ChatMessage objects to dict format for agent
            agent_messages = []
            for msg in messages:
                agent_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Gọi agent
            result = agent.invoke({"messages": agent_messages})
            
            # Extract response content
            if 'messages' in result and len(result['messages']) > 0:
                last_message = result['messages'][-1]
                return {
                    "role": "assistant",
                    "content": last_message.content if hasattr(last_message, 'content') else str(last_message)
                }
            else:
                return {
                    "role": "assistant", 
                    "content": "Xin lỗi, tôi không thể xử lý yêu cầu của bạn."
                }
                
        except Exception as e:
            raise Exception(f"Lỗi xử lý chat: {str(e)}")
    
    @staticmethod
    async def _process_file_attachment(file_attachment: Optional[UploadFile]) -> tuple[Optional[str], Optional[str]]:
        """
        Xử lý file attachment riêng biệt để tránh lỗi I/O
        
        Returns:
            tuple: (file_name, file_content)
        """
        if not file_attachment:
            return None, None
            
        file_name = file_attachment.filename or "unknown_file"
        file_content = None
        
        try:
            # Luôn cố gắng reset file pointer về đầu file và đọc ngay
            try:
                await file_attachment.seek(0)
            except Exception:
                pass
            
            try:
                file_bytes = await file_attachment.read()
            except Exception as read_error:
                # Thử seek rồi đọc lại một lần
                try:
                    await file_attachment.seek(0)
                    file_bytes = await file_attachment.read()
                except Exception:
                    file_content = f"[ERROR READING FILE: {file_name}] - {str(read_error)}"
                    return file_name, file_content
            
            # Đảm bảo file_bytes không rỗng
            if not file_bytes or len(file_bytes) == 0:
                file_content = f"[EMPTY FILE: {file_name}]"
            else:
                # Nếu là file ảnh
                if file_attachment.content_type and file_attachment.content_type.startswith('image/'):
                    # Tạo base64 string từ bytes cho future use
                    try:
                        base64_string = base64.b64encode(file_bytes).decode('utf-8')
                        file_content = f"[IMAGE: {file_name}] - Size: {len(file_bytes)} bytes, Content-Type: {file_attachment.content_type}"
                    except Exception as b64_error:
                        file_content = f"[IMAGE PROCESSING ERROR: {file_name}] - {str(b64_error)}"
                else:
                    # Nếu là text file, đọc content
                    try:
                        file_content = file_bytes.decode('utf-8')
                        # Giới hạn độ dài content để tránh message quá dài
                        if len(file_content) > 2000:
                            file_content = file_content[:2000] + "... (truncated)"
                    except UnicodeDecodeError:
                        # Thử với các encoding khác
                        try:
                            file_content = file_bytes.decode('latin-1')
                            if len(file_content) > 2000:
                                file_content = file_content[:2000] + "... (truncated)"
                        except Exception:
                            file_content = f"[BINARY FILE: {file_name}] - Size: {len(file_bytes)} bytes"
                        
        except Exception as file_error:
            # Log chi tiết lỗi để debug
            error_details = f"Type: {type(file_error).__name__}, Message: {str(file_error)}"
            file_content = f"[CRITICAL ERROR READING FILE: {file_name}] - {error_details}"
            
        finally:
            # Không đóng file tại đây để tránh ảnh hưởng tới lifecycle của framework
            pass
            
        return file_name, file_content

    @staticmethod
    async def process_agent_testcase_stream(
        conversation_id: Optional[str],
        title: str,
        pbi_requirement: str,
        file_attachment: Optional[UploadFile] = None,
        preloaded_file_name: Optional[str] = None,
        preloaded_file_content: Optional[str] = None,
        preloaded_base64_data: Optional[str] = None,
        preloaded_mime_type: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Xử lý agent testcase request với streaming response
        
        Args:
            conversation_id: Thread ID cho memory persistence
            title: Tiêu đề của testcase
            pbi_requirement: Yêu cầu PBI
            file_attachment: File đính kèm (nếu có)
            
        Yields:
            str: Server-Sent Events formatted strings
        """
        try:
            # Ưu tiên dùng nội dung file đã được preload ở endpoint
            if preloaded_file_name is not None or preloaded_file_content is not None:
                file_name, file_content = preloaded_file_name, preloaded_file_content
            else:
                # Nếu chưa preload, xử lý ngay đầu stream
                file_name, file_content = await ChatService._process_file_attachment(file_attachment)
            
            # Tạo message với context đầy đủ (không truyền file content)
            message_content = AgentManager.create_message_with_context(
                title=title,
                pbi_requirement=pbi_requirement,
                has_file=file_content is not None,
                file_name=file_name
            )
            
            # Lưu user message vào database nếu có conversation_id
            if conversation_id:
                db_manager.add_message(conversation_id, "user", message_content)
            
            # Tạo config cho agent với thread_id
            # Luôn cần thread_id để sử dụng memory checkpointer
            thread_id = conversation_id or f"temp_{int(time.time())}"
            config = {"configurable": {"thread_id": thread_id}}
            
            # Tạo message content cho agent (multimodal nếu có ảnh)
            agent_message = {"role": "user"}
            
            # Kiểm tra nếu có file ảnh thì tạo multimodal message
            if (file_content and file_name and 
                (file_content.startswith("[IMAGE:") or 
                 (preloaded_file_content and preloaded_file_content.startswith("[IMAGE:")))):
                
                # Sử dụng preloaded base64 data và mime type
                base64_data = preloaded_base64_data
                mime_type = preloaded_mime_type or "image/jpeg"  # default
                
                # Nếu có base64 data thì tạo multimodal message
                if base64_data:
                    agent_message["content"] = [
                        {
                            "type": "text",
                            "text": message_content,
                        },
                        {
                            "type": "image",
                            "source_type": "base64",
                            "data": base64_data,
                            "mime_type": mime_type,
                        },
                    ]
                else:
                    # Fallback to text only nếu không lấy được base64
                    agent_message["content"] = message_content
            else:
                # Message text thông thường nếu không có ảnh
                agent_message["content"] = message_content
            
            # Gọi agent với streaming và thread_id
            response = agent.astream(
                {"messages": [agent_message]},
                config=config
            )
            
            # Biến để lưu full response content
            full_response_content = ""
            
            # Stream từng chunk của response
            async for chunk in response:
                # Langgraph agent trả về structure: {'agent': {'messages': [...]}}
                if isinstance(chunk, dict):
                    # Kiểm tra structure của langgraph
                    if 'agent' in chunk and isinstance(chunk['agent'], dict):
                        agent_data = chunk['agent']
                        if 'messages' in agent_data:
                            for message in agent_data['messages']:
                                if hasattr(message, 'content') and message.content:
                                    # Lưu full content để save vào database sau
                                    full_response_content = message.content
                                    
                                    # Split content thành chunks nhỏ để tạo streaming effect
                                    content = message.content
                                    chunk_size = 50  # Chia nhỏ content
                                    
                                    for i in range(0, len(content), chunk_size):
                                        chunk_content = content[i:i + chunk_size]
                                        data = {
                                            "type": "chunk",
                                            "content": chunk_content,
                                            "role": "assistant",
                                            "conversation_id": conversation_id
                                        }
                                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                                        
                                        # Thêm delay nhỏ để tạo streaming effect
                                        await asyncio.sleep(0.05)
                    
                    # Fallback cho structure cũ
                    elif 'messages' in chunk:
                        for message in chunk['messages']:
                            if hasattr(message, 'content') and message.content:
                                full_response_content = message.content
                                data = {
                                    "type": "message",
                                    "content": message.content,
                                    "role": "assistant",
                                    "conversation_id": conversation_id
                                }
                                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # Lưu assistant response vào database nếu có conversation_id
            if conversation_id and full_response_content:
                db_manager.add_message(conversation_id, "assistant", full_response_content)
            
            # Gửi signal kết thúc stream
            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            # Gửi lỗi qua stream
            error_data = {
                "type": "error",
                "message": str(e),
                "conversation_id": conversation_id
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
