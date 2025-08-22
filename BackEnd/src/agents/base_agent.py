"""
Base Agent class định nghĩa interface chung cho tất cả agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel

from state import AgentState, AgentConfig
from utils import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class cho tất cả AI Agents
    Định nghĩa interface chung và shared functionality
    """
    
    def __init__(
        self,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        config: Optional[AgentConfig] = None,
        name: str = "BaseAgent"
    ):
        """
        Initialize base agent
        
        Args:
            llm: Language model instance
            tools: List of available tools
            config: Agent configuration
            name: Agent name
        """
        self.llm = llm
        self.tools = tools
        self.config = config or AgentConfig()
        self.name = name
        
        logger.info(f"Initialized {self.name} with {len(tools)} tools")
    
    @abstractmethod
    def create_graph(self) -> Any:
        """
        Create LangGraph instance for this agent
        
        Returns:
            LangGraph instance
        """
        pass
    
    @abstractmethod
    def process_message(self, message: str, state: AgentState) -> AgentState:
        """
        Process a single message và update state
        
        Args:
            message: Input message
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        pass
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool.name for tool in self.tools]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get tool descriptions for documentation"""
        return {tool.name: tool.description for tool in self.tools}
    
    def validate_config(self) -> bool:
        """Validate agent configuration"""
        try:
            # Basic validation
            if self.config.max_iterations <= 0:
                logger.error("max_iterations must be positive")
                return False
            
            if not (0.0 <= self.config.temperature <= 2.0):
                logger.error("temperature must be between 0.0 and 2.0")
                return False
            
            if self.config.timeout <= 0:
                logger.error("timeout must be positive")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return False
    
    def get_stats(self, state: AgentState) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_name": self.name,
            "tools_available": len(self.tools),
            "tools_used": len(state.tools_used),
            "iterations": state.iteration_count,
            "errors": state.error_count,
            "messages": len(state.messages)
        }
    
    def reset_state(self, state: AgentState) -> AgentState:
        """Reset agent state to initial values"""
        state.current_step = "start"
        state.iteration_count = 0
        state.tools_used = []
        state.tool_results = {}
        state.error_count = 0
        state.last_error = None
        state.is_complete = False
        state.needs_human_input = False
        state.custom_data = {}
        
        logger.info(f"Reset state for session {state.session_id}")
        return state
    
    def __str__(self) -> str:
        return f"{self.name}(tools={len(self.tools)})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', tools={len(self.tools)}, config={self.config})"
