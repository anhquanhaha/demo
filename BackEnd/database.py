"""
Database setup và models cho SQLite
"""

import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

class DatabaseManager:
    """Manager class để xử lý SQLite database"""
    
    def __init__(self, db_path: str = "testcase_agent.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database và tạo tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tạo table requests
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    pbi_requirement TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tạo table messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES requests (conversation_id)
                )
            """)
            
            # Tạo index cho performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_id 
                ON messages (conversation_id)
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager để quản lý database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Để có thể access columns by name
        try:
            yield conn
        finally:
            conn.close()
    
    def create_request(self, title: str, pbi_requirement: str) -> Dict[str, Any]:
        """Tạo request mới"""
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO requests (conversation_id, title, pbi_requirement)
                VALUES (?, ?, ?)
            """, (conversation_id, title, pbi_requirement))
            
            request_id = cursor.lastrowid
            conn.commit()
            
            # Lấy request vừa tạo
            cursor.execute("""
                SELECT * FROM requests WHERE id = ?
            """, (request_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Lấy tất cả requests"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM requests 
                ORDER BY updated_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_request_by_conversation_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Lấy request theo conversation_id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM requests WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_request_timestamp(self, conversation_id: str):
        """Cập nhật timestamp của request"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE requests 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE conversation_id = ?
            """, (conversation_id,))
            conn.commit()
    
    def add_message(self, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
        """Thêm message vào conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
            """, (conversation_id, role, content))
            
            message_id = cursor.lastrowid
            conn.commit()
            
            # Cập nhật timestamp của request
            self.update_request_timestamp(conversation_id)
            
            # Lấy message vừa tạo
            cursor.execute("""
                SELECT * FROM messages WHERE id = ?
            """, (message_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_messages_by_conversation_id(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Lấy tất cả messages của một conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY created_at ASC
            """, (conversation_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def delete_request(self, conversation_id: str) -> bool:
        """Xóa request và tất cả messages liên quan"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Xóa messages trước
            cursor.execute("""
                DELETE FROM messages WHERE conversation_id = ?
            """, (conversation_id,))
            
            # Xóa request
            cursor.execute("""
                DELETE FROM requests WHERE conversation_id = ?
            """, (conversation_id,))
            
            conn.commit()
            return cursor.rowcount > 0

# Singleton instance
db_manager = DatabaseManager()
