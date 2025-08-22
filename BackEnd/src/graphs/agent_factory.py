"""
Factory class để tạo các loại agents khác nhau
"""
from typing import List, Optional, Type
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel

try:
    from langchain_openai import ChatOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from langchain_community.llms.fake import FakeListLLM
    HAS_FAKE_LLM = True
except ImportError:
    HAS_FAKE_LLM = False

from agents import BaseAgent, ReactAgent
from state import AgentConfig
from tools import ToolRegistry
from utils import get_logger, get_config

logger = get_logger(__name__)


class AgentFactory:
    """
    Factory pattern để tạo và quản lý agents
    Hỗ trợ tạo các loại agents khác nhau với configuration linh hoạt
    """
    
    def __init__(self):
        self.config = get_config()
        self.tool_registry = ToolRegistry()
        logger.info("AgentFactory initialized")
    
    def create_llm(self, model_type: str = "auto") -> BaseLanguageModel:
        """
        Create LLM instance based on configuration
        
        Args:
            model_type: Type of model ("openai", "fake", "auto")
            
        Returns:
            LLM instance
        """
        if model_type == "auto":
            # Auto-detect based on API key availability
            if self.config.has_openai_key() and HAS_OPENAI:
                model_type = "openai"
            elif HAS_FAKE_LLM:
                model_type = "fake"
            else:
                raise RuntimeError("No suitable LLM available")
        
        if model_type == "openai":
            if not HAS_OPENAI:
                raise ImportError("langchain-openai not installed")
            
            if not self.config.has_openai_key():
                raise ValueError("OpenAI API key not configured")
            
            logger.info("Creating ChatOpenAI LLM")
            return ChatOpenAI(
                model=self.config.get("llm.model", "gpt-3.5-turbo"),
                temperature=self.config.get("llm.temperature", 0.1),
                max_tokens=self.config.get("llm.max_tokens"),
                timeout=self.config.get("llm.timeout", 30),
                openai_api_key=self.config.get("api.openai_api_key")
            )
        
        elif model_type == "fake":
            if not HAS_FAKE_LLM:
                raise ImportError("langchain-community not available")
            
            logger.info("Creating FakeListLLM for demo")
            return FakeListLLM(responses=[
                "Tôi là AI Agent được tạo bởi LangGraph. Tôi có thể giúp bạn với nhiều tác vụ khác nhau!",
                "Để sử dụng đầy đủ tính năng, hãy cấu hình OpenAI API key.",
                "Bạn có thể hỏi tôi về thời gian, tính toán, hoặc thời tiết.",
                "Tôi sẵn sàng hỗ trợ bạn!" 
            ])
        
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
    
    def get_tools(self, tool_categories: Optional[List[str]] = None) -> List[BaseTool]:
        """
        Get tools from registry
        
        Args:
            tool_categories: List of tool categories to include (None = all)
            
        Returns:
            List of tools
        """
        if tool_categories is None:
            return self.tool_registry.get_all_tools()
        
        tools = []
        for category in tool_categories:
            tools.extend(self.tool_registry.get_tools_by_category(category))
        
        return tools
    
    def create_react_agent(
        self,
        model_type: str = "auto",
        tool_categories: Optional[List[str]] = None,
        config: Optional[AgentConfig] = None,
        enable_memory: bool = True
    ) -> ReactAgent:
        """
        Create ReAct Agent
        
        Args:
            model_type: LLM type to use
            tool_categories: Tool categories to include
            config: Agent configuration
            enable_memory: Enable conversation memory
            
        Returns:
            ReactAgent instance
        """
        logger.info(f"Creating ReAct Agent with model_type={model_type}")
        
        try:
            # Create LLM
            llm = self.create_llm(model_type)
            
            # Get tools
            tools = self.get_tools(tool_categories)
            logger.info(f"Loaded {len(tools)} tools")
            
            # Create config if not provided
            if config is None:
                config = AgentConfig(
                    model=self.config.get("llm.model", "gpt-3.5-turbo"),
                    temperature=self.config.get("llm.temperature", 0.1),
                    max_iterations=self.config.get("agent.max_iterations", 10),
                    memory_enabled=enable_memory,
                    thread_id=self.config.get("agent.default_thread_id", "default")
                )
            
            # Create agent
            agent = ReactAgent(
                llm=llm,
                tools=tools,
                config=config,
                enable_memory=enable_memory
            )
            
            logger.info("ReAct Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create ReAct Agent: {e}")
            raise
    
    def create_agent(
        self,
        agent_type: str = "react",
        **kwargs
    ) -> BaseAgent:
        """
        Generic agent creation method
        
        Args:
            agent_type: Type of agent to create ("react", etc.)
            **kwargs: Arguments for specific agent type
            
        Returns:
            Agent instance
        """
        if agent_type == "react":
            return self.create_react_agent(**kwargs)
        else:
            raise ValueError(f"Unknown agent_type: {agent_type}")
    
    def list_available_models(self) -> List[str]:
        """List available LLM models"""
        models = []
        
        if HAS_FAKE_LLM:
            models.append("fake")
        
        if HAS_OPENAI and self.config.has_openai_key():
            models.append("openai")
        
        return models
    
    def get_factory_info(self) -> dict:
        """Get factory configuration info"""
        return {
            "available_models": self.list_available_models(),
            "available_tools": self.tool_registry.list_tools(),
            "has_openai_key": self.config.has_openai_key(),
            "debug_mode": self.config.is_debug()
        }
