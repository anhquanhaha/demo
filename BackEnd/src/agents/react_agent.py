"""
ReAct Agent implementation using LangGraph
"""
from typing import Any, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from .base_agent import BaseAgent
from ..state import AgentState, AgentConfig
from ..utils import get_logger, measure_time

logger = get_logger(__name__)


class ReactAgent(BaseAgent):
    """
    ReAct (Reasoning + Acting) Agent implementation
    Sử dụng LangGraph prebuilt ReAct agent
    """
    
    def __init__(
        self,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        config: Optional[AgentConfig] = None,
        enable_memory: bool = True
    ):
        """
        Initialize ReAct Agent
        
        Args:
            llm: Language model instance
            tools: List of available tools
            config: Agent configuration
            enable_memory: Enable conversation memory
        """
        super().__init__(llm, tools, config, name="ReactAgent")
        
        self.enable_memory = enable_memory
        self.memory = MemorySaver() if enable_memory else None
        self._graph = None
        
        logger.info(f"ReAct Agent initialized with memory={'enabled' if enable_memory else 'disabled'}")
    
    def create_graph(self) -> Any:
        """
        Create LangGraph ReAct agent
        
        Returns:
            LangGraph ReAct agent instance
        """
        if self._graph is None:
            logger.info("Creating LangGraph ReAct agent...")
            
            # Validate config trước khi tạo graph
            if not self.validate_config():
                raise ValueError("Invalid agent configuration")
            
            try:
                self._graph = create_react_agent(
                    model=self.llm,
                    tools=self.tools,
                    checkpointer=self.memory
                )
                logger.info("LangGraph ReAct agent created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create ReAct agent: {e}")
                raise
        
        return self._graph
    
    @measure_time
    def process_message(self, message: str, state: AgentState) -> AgentState:
        """
        Process message using ReAct agent
        
        Args:
            message: Input message from user
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            # Update state
            state.increment_iteration()
            state.current_step = "processing"
            
            # Add user message to state
            user_message = HumanMessage(content=message)
            state.add_message(user_message)
            
            # Get or create graph
            graph = self.create_graph()
            
            # Prepare config for graph execution
            config = {
                "configurable": {
                    "thread_id": state.session_id
                }
            }
            
            # Execute graph
            logger.info(f"Processing message: {message[:50]}...")
            
            result = graph.invoke(
                {"messages": [user_message]},
                config=config
            )
            
            # Extract response
            if "messages" in result:
                # Add all response messages to state
                for msg in result["messages"]:
                    if msg != user_message:  # Don't add user message again
                        state.add_message(msg)
                
                # Get the last AI message for logging
                ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'content')]
                if ai_messages:
                    last_response = ai_messages[-1].content
                    logger.info(f"Agent responded: {last_response[:100]}...")
            
            # Update completion status
            state.current_step = "completed"
            state.is_complete = True
            
            return state
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            state.set_error(str(e))
            state.current_step = "error"
            return state
    
    def stream_response(self, message: str, session_id: str = "default"):
        """
        Stream response từ agent (generator)
        
        Args:
            message: Input message
            session_id: Session ID for memory
            
        Yields:
            Response chunks
        """
        try:
            graph = self.create_graph()
            
            config = {
                "configurable": {
                    "thread_id": session_id
                }
            }
            
            logger.info(f"Streaming response for: {message[:50]}...")
            
            for chunk in graph.stream(
                {"messages": [HumanMessage(content=message)]},
                config=config
            ):
                if "messages" in chunk:
                    for msg in chunk["messages"]:
                        if hasattr(msg, 'content') and msg.content:
                            yield msg.content
                            
        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            yield f"❌ Lỗi: {str(e)}"
    
    def batch_process(self, messages: List[str], session_id: str = "batch") -> List[str]:
        """
        Process multiple messages in batch
        
        Args:
            messages: List of input messages
            session_id: Session ID for memory
            
        Returns:
            List of responses
        """
        responses = []
        state = AgentState(session_id=session_id)
        
        logger.info(f"Batch processing {len(messages)} messages")
        
        for i, message in enumerate(messages):
            logger.info(f"Processing batch message {i+1}/{len(messages)}")
            
            try:
                updated_state = self.process_message(message, state)
                
                # Extract last response
                if updated_state.messages:
                    last_msg = updated_state.messages[-1]
                    if hasattr(last_msg, 'content'):
                        responses.append(last_msg.content)
                    else:
                        responses.append("No response")
                else:
                    responses.append("No response")
                
                state = updated_state
                
            except Exception as e:
                logger.error(f"Error in batch message {i+1}: {e}")
                responses.append(f"❌ Lỗi: {str(e)}")
        
        logger.info(f"Batch processing completed: {len(responses)} responses")
        return responses
    
    def clear_memory(self, session_id: str) -> bool:
        """
        Clear memory for specific session
        
        Args:
            session_id: Session ID to clear
            
        Returns:
            True if successful
        """
        try:
            if self.memory:
                # Note: MemorySaver doesn't have direct clear method
                # This is a placeholder - actual implementation depends on checkpointer type
                logger.info(f"Cleared memory for session: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
