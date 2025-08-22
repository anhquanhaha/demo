# 🤖 Test Case AI Agent

Ứng dụng tạo và quản lý test cases tự động với AI Agent, sử dụng FastAPI backend và HTML/CSS/JavaScript frontend.

## ✨ Tính năng chính

### 🎯 **Quản lý yêu cầu**
- Tạo, xem, xóa yêu cầu test case
- Lưu trữ persistent với SQLite
- Tìm kiếm và lọc yêu cầu
- Auto-generate Conversation ID

### 🤖 **AI Agent Integration**
- Streaming response real-time
- Memory persistence qua conversations
- Hỗ trợ file attachment (ảnh, text, JSON, XML, MD)
- Phân tích yêu cầu PBI chi tiết

### 💬 **Chat Interface**
- Giao diện chat trực quan
- Lịch sử tin nhắn đầy đủ
- Export conversation sang Markdown
- Real-time status indicators

## 🏗️ Kiến trúc hệ thống

```
demo/
├── BackEnd/                 # FastAPI Backend
│   ├── main.py             # Main FastAPI application
│   ├── agent.py            # LangGraph AI Agent
│   ├── database.py         # SQLite database manager
│   ├── Model/              # Pydantic models
│   │   ├── chat_models.py
│   │   ├── item_models.py
│   │   └── request_models.py
│   ├── Service/            # Business logic
│   │   └── chat_service.py
│   └── requirements.txt    # Python dependencies
├── UI/                     # Frontend
│   ├── index.html         # Trang tổng quan
│   ├── pages/
│   │   └── detail.html    # Trang chi tiết yêu cầu
│   ├── css/
│   │   └── style.css      # Styles chung
│   └── js/
│       ├── api.js         # API client
│       └── utils.js       # Utility functions
└── README.md
```

## 🚀 Cài đặt và chạy

### 1. **Cài đặt Backend**

```bash
cd BackEnd
pip install -r requirements.txt
```

### 2. **Cấu hình Environment**

Tạo file `.env` trong thư mục `BackEnd`:

```env
MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. **Chạy Backend Server**

```bash
python main.py
```

Server sẽ chạy tại: `http://localhost:8000`

### 4. **Mở Frontend**

Mở file `UI/index.html` trong trình duyệt hoặc serve qua HTTP server:

```bash
# Với Python
cd UI
python -m http.server 3000

# Với Node.js
npx serve UI -p 3000
```

## 📖 Hướng dẫn sử dụng

### **Màn hình tổng quan**
1. Mở `UI/index.html`
2. Xem danh sách các yêu cầu hiện có
3. Nhấn "Tạo yêu cầu mới" để tạo yêu cầu
4. Click vào yêu cầu để xem chi tiết

### **Màn hình chi tiết**
1. Xem thông tin yêu cầu bên trái
2. Upload file đính kèm (tùy chọn)
3. Nhấn "Gửi cho AI Agent" để bắt đầu
4. Xem response streaming real-time
5. Export cuộc trò chuyện sang file Markdown

## 🔧 API Endpoints

### **Request Management**
- `GET /requests` - Lấy tất cả requests
- `POST /requests` - Tạo request mới
- `GET /requests/{conversation_id}` - Lấy request theo ID
- `GET /requests/{conversation_id}/messages` - Lấy messages
- `DELETE /requests/{conversation_id}` - Xóa request

### **AI Agent**
- `POST /agent-testcase` - Gửi request tới AI Agent (streaming)
- `POST /chat` - Chat endpoint thông thường

### **Utility**
- `GET /` - Welcome endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger)

## 🎨 Giao diện

### **Responsive Design**
- Desktop-first với mobile support
- Modern gradient backgrounds
- Card-based layout
- Smooth animations và transitions

### **Components**
- Modal dialogs
- Toast notifications
- Loading states
- Empty states
- Status indicators
- File upload interface

## 🛠️ Công nghệ sử dụng

### **Backend**
- **FastAPI** - Web framework
- **LangGraph** - AI Agent framework
- **LangChain** - LLM integration
- **SQLite** - Database
- **Pydantic** - Data validation
- **OpenAI GPT** - Language model

### **Frontend**
- **Vanilla HTML/CSS/JavaScript** - No frameworks
- **CSS Grid & Flexbox** - Layout
- **Fetch API** - HTTP requests
- **Server-Sent Events** - Streaming

## 📊 Database Schema

### **requests table**
```sql
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    pbi_requirement TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **messages table**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES requests (conversation_id)
);
```

## 🔍 Tính năng nâng cao

### **Memory Persistence**
- AI Agent nhớ context qua conversations
- Thread-based memory với LangGraph
- Lưu trữ local với MemorySaver

### **File Processing**
- Hỗ trợ upload ảnh (base64 encoding)
- Text files (UTF-8 decoding)
- Binary files (size info only)
- Error handling cho file corrupted

### **Streaming Response**
- Server-Sent Events (SSE)
- Real-time chunk processing
- Artificial streaming effect (50 chars/chunk)
- Progress indicators

## 🚨 Lưu ý quan trọng

1. **CORS**: Server cho phép tất cả origins (`*`) - chỉ dùng cho development
2. **File Size**: Không giới hạn file size - nên thêm validation
3. **Security**: Không có authentication - chỉ dùng cho demo
4. **Database**: SQLite file sẽ được tạo tự động khi chạy lần đầu
5. **OpenAI API**: Cần API key hợp lệ để AI Agent hoạt động

## 🎯 Demo Flow

1. **Tạo yêu cầu**: "Màn hình đăng nhập"
2. **Nhập PBI**: Mô tả chi tiết requirements
3. **Upload mockup**: Ảnh giao diện (tùy chọn)
4. **Gửi AI Agent**: Nhận phân tích và test cases
5. **Export**: Lưu cuộc trò chuyện ra file

## 📝 Ví dụ sử dụng

### **Input mẫu:**
- **Tiêu đề**: Màn hình đăng nhập
- **PBI Requirement**: 
  ```
  Yêu cầu của màn hình đăng nhập:
  1. Có form nhập username và password
  2. Có nút đăng nhập
  3. Có chức năng "Quên mật khẩu"
  4. Validate input trước khi submit
  5. Hiển thị thông báo lỗi nếu đăng nhập thất bại
  ```
- **File đính kèm**: login_mockup.png

### **Output mẫu:**
AI Agent sẽ phân tích và đưa ra:
- Test cases chi tiết
- Edge cases cần kiểm tra
- Gợi ý cải thiện UX/UI
- Câu hỏi làm rõ requirements

---

**Phát triển bởi**: Test Case AI Agent Team  
**Version**: 1.0.0  
**License**: MIT