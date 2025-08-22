# 🚀 Hướng Dẫn Setup và Chạy AI Agent (Refactored)

## 📋 Yêu Cầu Hệ Thống
- Python 3.13
- PDM (Python Dependency Manager)
- OpenAI API Key (tùy chọn, có fallback mode)

## 🏗️ Kiến Trúc Mới (Modular Design)

Dự án đã được refactor thành kiến trúc modular:

```
src/
├── agents/          # Base agent classes và implementations
│   ├── base_agent.py      # Abstract base cho tất cả agents
│   └── react_agent.py     # ReAct agent implementation
├── graphs/          # Graph management và factories
│   ├── agent_factory.py   # Factory pattern tạo agents
│   └── graph_runner.py    # Orchestrate chạy agents
├── state/           # State management với Pydantic
│   └── agent_state.py     # AgentState và AgentConfig
├── tools/           # Tool definitions và registry
│   ├── basic_tools.py     # Basic tools (time, calc, weather)
│   └── tool_registry.py   # Tool management system
├── utils/           # Utilities và helpers
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging utilities
│   └── helpers.py         # Helper functions
└── main.py          # Clean entry point
```

## ⚙️ Cài Đặt Dependencies

1. **Cài đặt dependencies:**
```bash
pdm install
```

2. **Kích hoạt virtual environment:**
```bash
pdm shell
```

## 🔑 Cấu Hình OpenAI API (Tùy chọn)

```bash
# Windows
set OPENAI_API_KEY=your-actual-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-actual-api-key-here
```

## 🎮 Chạy Agent

```bash
cd src
python main.py
```

## 🎯 Modes Hoạt Động (Đã Mở Rộng)

1. **Interactive Mode** - Chat liên tục với agent
2. **Single Task** - Xử lý một task cụ thể
3. **Batch Tasks** - Xử lý nhiều tasks cùng lúc  
4. **Demo Mode** - Chạy thử với tasks mẫu
5. **Info & Stats** - Xem thông tin hệ thống

## 🔧 Tools Được Tích Hợp

### Basic Tools:
- **get_current_time** - Thời gian hiện tại
- **calculator** - Tính toán an toàn với validation
- **get_weather** - Thời tiết cho Hà Nội, TP.HCM, Đà Nẵng

### Tool Registry System:
- Quản lý tools theo categories
- Dễ dàng thêm/xóa tools
- Tool discovery và documentation

## 🏛️ Kiến Trúc Pattern

### 1. **Factory Pattern** (`AgentFactory`)
```python
factory = AgentFactory()
agent = factory.create_react_agent(model_type="auto")
```

### 2. **Strategy Pattern** (`BaseAgent`)
```python
class CustomAgent(BaseAgent):
    def create_graph(self):
        # Custom implementation
        pass
```

### 3. **Registry Pattern** (`ToolRegistry`)
```python
registry = ToolRegistry()
registry.register_tool("my_tool", my_tool_func, "category")
```

### 4. **State Management** (`AgentState`)
```python
state = AgentState(session_id="user123")
state.add_message(message)
state.add_tool_usage("calculator", result)
```

## 🔄 Mở Rộng Hệ Thống

### Thêm Tools Mới:

1. **Tạo tool trong `tools/`:**
```python
@tool
def my_custom_tool(param: str) -> str:
    """My custom tool description"""
    return f"Result: {param}"
```

2. **Đăng ký trong ToolRegistry:**
```python
registry.register_tool("my_custom_tool", my_custom_tool, "custom")
```

### Thêm Agent Type Mới:

1. **Extend BaseAgent:**
```python
class MyAgent(BaseAgent):
    def create_graph(self):
        # Implementation
        pass
    
    def process_message(self, message, state):
        # Implementation
        pass
```

2. **Update AgentFactory:**
```python
def create_my_agent(self, **kwargs):
    return MyAgent(...)
```

### Custom Configuration:

```python
config = AgentConfig(
    model="gpt-4",
    temperature=0.7,
    max_iterations=15,
    enable_calculator=True
)
```

## 📊 Logging & Monitoring

```python
from utils import get_logger

logger = get_logger(__name__)
logger.info("Custom message")
```

## 🧪 Testing

### Test Tools:
```python
from tools import calculator
result = calculator("2 + 3")
assert "5" in result
```

### Test Agent:
```python
factory = AgentFactory()
agent = factory.create_react_agent("fake")
state = AgentState(session_id="test")
updated_state = agent.process_message("Hello", state)
```

## 🔧 Troubleshooting

### Import Errors:
```bash
# Sync dependencies
pdm sync

# Check Python path
cd src && python -c "import tools; print('OK')"
```

### Configuration Issues:
```python
from utils import get_config
config = get_config()
print(config.to_dict())
```

## 💡 Best Practices

1. **Separation of Concerns** - Mỗi module có responsibility riêng
2. **Dependency Injection** - Inject dependencies through constructors
3. **Configuration Management** - Centralized config với environment overrides
4. **Error Handling** - Comprehensive error handling ở mọi tầng
5. **Logging** - Structured logging với proper levels
6. **State Management** - Immutable state transitions với Pydantic validation

## 📈 Performance & Scalability

- **Memory Management** - Session-based memory với cleanup
- **Tool Registry** - Lazy loading và caching
- **Streaming Responses** - Non-blocking UI updates  
- **Batch Processing** - Efficient multi-task handling
- **Configuration Caching** - Runtime config optimization

Để biết thêm chi tiết, tham khảo [LangGraph Documentation](https://langchain-ai.github.io/langgraph/).
