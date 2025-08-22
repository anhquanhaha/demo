"""
Graph Runner để orchestrate việc chạy agents với các modes khác nhau
"""
from typing import List, Optional, Dict, Any, Iterator
from agents import BaseAgent
from state import AgentState
from utils import get_logger, Timer, format_response

logger = get_logger(__name__)


class GraphRunner:
    """
    Runner class để orchestrate việc chạy agents
    Hỗ trợ các modes: interactive, single_task, batch
    """
    
    def __init__(self, agent: BaseAgent):
        """
        Initialize GraphRunner
        
        Args:
            agent: Agent instance to run
        """
        self.agent = agent
        self.current_state = None
        logger.info(f"GraphRunner initialized with {agent.name}")
    
    def run_interactive(self, session_id: str = "interactive") -> None:
        """
        Chạy agent ở interactive mode
        
        Args:
            session_id: Session ID for memory
        """
        logger.info(f"Starting interactive mode for session {session_id}")
        
        # Initialize state
        self.current_state = AgentState(
            session_id=session_id,
            agent_name=self.agent.name
        )
        
        # Welcome message
        print("🤖 AI Agent đã sẵn sàng! (Gõ 'quit', 'exit', hoặc 'q' để thoát)")
        print("💡 Bạn có thể hỏi về:")
        
        # Show available tools
        tool_descriptions = self.agent.get_tool_descriptions()
        for tool_name, description in tool_descriptions.items():
            print(f"   - {description}")
        
        print("-" * 50)
        
        try:
            while True:
                # Get user input
                user_input = input("\n👤 Bạn: ").strip()
                
                # Check exit commands
                if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
                    print("👋 Tạm biệt!")
                    break
                
                if not user_input:
                    continue
                
                # Process message
                print("🤖 Agent: ", end="", flush=True)
                
                try:
                    # Use streaming if available
                    if hasattr(self.agent, 'stream_response'):
                        response_parts = []
                        for chunk in self.agent.stream_response(user_input, session_id):
                            print(chunk, end="", flush=True)
                            response_parts.append(chunk)
                        print()  # New line
                        
                        # Update state with full response
                        full_response = "".join(response_parts)
                        # Note: State update would be handled inside the agent
                        
                    else:
                        # Fallback to regular processing
                        self.current_state = self.agent.process_message(user_input, self.current_state)
                        
                        if self.current_state.messages:
                            last_message = self.current_state.messages[-1]
                            if hasattr(last_message, 'content'):
                                print(last_message.content)
                        else:
                            print("Không có phản hồi")
                            
                except KeyboardInterrupt:
                    print("\n👋 Tạm biệt!")
                    break
                except Exception as e:
                    logger.error(f"Error in interactive mode: {e}")
                    print(f"\n❌ Lỗi: {e}")
                    
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
        
        # Log final stats
        if self.current_state:
            stats = self.agent.get_stats(self.current_state)
            logger.info(f"Interactive session ended: {stats}")
    
    def run_single_task(self, task: str, session_id: str = "single_task") -> str:
        """
        Chạy một task đơn lẻ
        
        Args:
            task: Task description
            session_id: Session ID for memory
            
        Returns:
            Response string
        """
        logger.info(f"Running single task: {task[:50]}...")
        
        with Timer(f"Single task: {task[:30]}..."):
            try:
                # Initialize state
                state = AgentState(
                    session_id=session_id,
                    agent_name=self.agent.name
                )
                
                # Process task
                updated_state = self.agent.process_message(task, state)
                
                # Extract response
                if updated_state.messages:
                    last_message = updated_state.messages[-1]
                    if hasattr(last_message, 'content'):
                        response = last_message.content
                    else:
                        response = "Không có phản hồi"
                else:
                    response = "Không có phản hồi"
                
                # Log stats
                stats = self.agent.get_stats(updated_state)
                logger.info(f"Task completed: {stats}")
                
                return response
                
            except Exception as e:
                error_msg = f"Lỗi xử lý task: {str(e)}"
                logger.error(error_msg)
                return error_msg
    
    def run_batch(
        self, 
        tasks: List[str], 
        session_id: str = "batch",
        show_progress: bool = True
    ) -> List[str]:
        """
        Chạy batch tasks
        
        Args:
            tasks: List of tasks
            session_id: Session ID for memory
            show_progress: Show progress indicators
            
        Returns:
            List of responses
        """
        logger.info(f"Running batch of {len(tasks)} tasks")
        
        responses = []
        
        with Timer(f"Batch processing {len(tasks)} tasks"):
            if hasattr(self.agent, 'batch_process'):
                # Use agent's batch processing if available
                responses = self.agent.batch_process(tasks, session_id)
            else:
                # Process one by one
                for i, task in enumerate(tasks):
                    if show_progress:
                        print(f"🔄 Processing task {i+1}/{len(tasks)}: {task[:50]}...")
                    
                    response = self.run_single_task(
                        task, 
                        session_id=f"{session_id}_task_{i}"
                    )
                    responses.append(response)
        
        logger.info(f"Batch processing completed: {len(responses)} responses")
        return responses
    
    def run_demo(self) -> None:
        """Chạy demo nhanh với các tasks mẫu"""
        
        demo_tasks = [
            "Bây giờ là mấy giờ?",
            "Tính 15 * 7 + 23",
            "Thời tiết Hà Nội thế nào?"
        ]
        
        print("🎮 Chạy Demo Mode")
        print("=" * 40)
        
        for i, task in enumerate(demo_tasks, 1):
            print(f"\n🔸 Demo {i}: {task}")
            print("-" * 30)
            
            response = self.run_single_task(task, f"demo_task_{i}")
            print(f"🤖 Kết quả: {response}")
            
            if i < len(demo_tasks):
                print()  # Space between demos
        
        print("\n✅ Demo hoàn tất!")
    
    def get_session_stats(self) -> Optional[Dict[str, Any]]:
        """Get current session statistics"""
        if self.current_state:
            return self.agent.get_stats(self.current_state)
        return None
    
    def reset_session(self, session_id: str = "default") -> None:
        """Reset current session"""
        if self.current_state:
            self.current_state = self.agent.reset_state(self.current_state)
            self.current_state.session_id = session_id
            logger.info(f"Session reset: {session_id}")
    
    def export_conversation(self) -> Optional[List[Dict[str, Any]]]:
        """Export conversation history"""
        if not self.current_state or not self.current_state.messages:
            return None
        
        conversation = []
        for msg in self.current_state.messages:
            conversation.append({
                "type": msg.__class__.__name__,
                "content": getattr(msg, 'content', str(msg)),
                "timestamp": getattr(msg, 'timestamp', None)
            })
        
        return conversation
