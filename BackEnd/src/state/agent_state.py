"""
Agent State definitions using Pydantic
"""
from typing import Annotated, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class AgentConfig(BaseModel):
    """Configuration cho Agent"""
    
    model: str = Field(default="gpt-3.5-turbo", description="LLM model name")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for LLM")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens for response")
    
    # Tool configuration
    enable_calculator: bool = Field(default=True, description="Enable calculator tool")
    enable_weather: bool = Field(default=True, description="Enable weather tool")
    enable_time: bool = Field(default=True, description="Enable time tool")
    
    # Agent behavior
    max_iterations: int = Field(default=10, ge=1, le=50, description="Max iterations for agent")
    timeout: int = Field(default=30, ge=5, le=300, description="Timeout in seconds")
    
    # Memory settings
    memory_enabled: bool = Field(default=True, description="Enable conversation memory")
    thread_id: str = Field(default="default", description="Thread ID for memory")
    
    class Config:
        """Pydantic config"""
        extra = "forbid"  # Không cho phép fields không được định nghĩa
        validate_assignment = True  # Validate khi assign giá trị mới


class AgentState(BaseModel):
    """
    State của Agent trong LangGraph
    Đây là TypedDict-like structure để LangGraph có thể track state
    """
    
    # Core conversation
    messages: List[BaseMessage] = Field(default_factory=list, description="Conversation messages")
    
    # Agent metadata
    agent_name: str = Field(default="AIAgent", description="Name of the agent")
    session_id: str = Field(default="default", description="Session identifier")
    
    # Processing state
    current_step: str = Field(default="start", description="Current processing step")
    iteration_count: int = Field(default=0, description="Number of iterations")
    
    # Tool usage tracking
    tools_used: List[str] = Field(default_factory=list, description="List of tools used")
    tool_results: Dict[str, Any] = Field(default_factory=dict, description="Results from tools")
    
    # Error handling
    error_count: int = Field(default=0, description="Number of errors encountered")
    last_error: Optional[str] = Field(default=None, description="Last error message")
    
    # Status flags
    is_complete: bool = Field(default=False, description="Whether processing is complete")
    needs_human_input: bool = Field(default=False, description="Whether human input is needed")
    
    # Custom data storage
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data storage")
    
    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True  # Cho phép các types như BaseMessage
        extra = "forbid"
        validate_assignment = True
    
    def add_message(self, message: BaseMessage) -> None:
        """Add message to conversation"""
        self.messages.append(message)
    
    def increment_iteration(self) -> None:
        """Increment iteration counter"""
        self.iteration_count += 1
    
    def add_tool_usage(self, tool_name: str, result: Any = None) -> None:
        """Track tool usage"""
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)
        
        if result is not None:
            self.tool_results[tool_name] = result
    
    def set_error(self, error_message: str) -> None:
        """Set error state"""
        self.error_count += 1
        self.last_error = error_message
    
    def reset_error(self) -> None:
        """Clear error state"""
        self.last_error = None
    
    def is_max_iterations(self, max_iter: int) -> bool:
        """Check if max iterations reached"""
        return self.iteration_count >= max_iter
    
    def get_summary(self) -> Dict[str, Any]:
        """Get state summary for logging"""
        return {
            "session_id": self.session_id,
            "current_step": self.current_step,
            "iteration_count": self.iteration_count,
            "tools_used": self.tools_used,
            "error_count": self.error_count,
            "is_complete": self.is_complete,
            "message_count": len(self.messages)
        }
