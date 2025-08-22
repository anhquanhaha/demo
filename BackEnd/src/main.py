"""
AI Agent với LangGraph - Main Application Entry Point
"""
import sys
from typing import Optional

# Import modules from our architecture
from graphs import AgentFactory, GraphRunner
from utils import setup_logger, load_config, get_logger
from state import AgentConfig

# Setup logging
logger = setup_logger("AIAgent", level="INFO")


class AIAgentApp:
    """Main Application class"""
    
    def __init__(self):
        """Initialize application"""
        self.config = load_config()
        self.factory = AgentFactory()
        self.runner = None
        self.agent = None
        
        logger.info("AI Agent Application initialized")
    
    def initialize_agent(self, model_type: str = "auto") -> bool:
        """
        Initialize agent with specified model type
        
        Args:
            model_type: Model type ("auto", "openai", "fake")
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating agent with model_type: {model_type}")
            
            # Create agent using factory
            self.agent = self.factory.create_react_agent(
                model_type=model_type,
                enable_memory=True
            )
            
            # Create runner
            self.runner = GraphRunner(self.agent)
            
            logger.info("Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            print(f"❌ Lỗi khởi tạo agent: {e}")
            return False
    
    def show_welcome_message(self):
        """Show welcome and info"""
        print("🚀 AI Agent với LangGraph")
        print("=" * 40)
        
        # Show factory info
        factory_info = self.factory.get_factory_info()
        
        print(f"🔧 Models khả dụng: {', '.join(factory_info['available_models'])}")
        print(f"🛠️  Tools có sẵn: {len(factory_info['available_tools'])}")
        print(f"🔑 OpenAI API: {'✅' if factory_info['has_openai_key'] else '❌'}")
        
        if not factory_info['has_openai_key']:
            print("💡 Để sử dụng ChatGPT, set OPENAI_API_KEY environment variable")
        
        print()
    
    def show_menu(self) -> str:
        """Show main menu and get user choice"""
        print("📋 Chọn mode hoạt động:")
        print("1. Interactive (tương tác liên tục)")  
        print("2. Single Task (xử lý task đơn)")
        print("3. Batch Tasks (xử lý nhiều tasks)")
        print("4. Demo nhanh")
        print("5. Info & Stats")
        print("0. Thoát")
        
        return input("👉 Lựa chọn (0-5): ").strip()
    
    def run_interactive_mode(self):
        """Run interactive mode"""
        print("\n🔄 Chuyển sang Interactive Mode...")
        self.runner.run_interactive()
    
    def run_single_task_mode(self):
        """Run single task mode"""
        task = input("\n👉 Nhập task cần xử lý: ").strip()
        if not task:
            print("❌ Task không được để trống")
            return
        
        print("\n🎯 Xử lý single task...")
        response = self.runner.run_single_task(task)
        print(f"\n🤖 Kết quả: {response}")
    
    def run_batch_mode(self):
        """Run batch tasks mode"""
        print("\n📝 Nhập các tasks (mỗi dòng một task, dòng trống để kết thúc):")
        
        tasks = []
        while True:
            task = input(f"Task {len(tasks)+1}: ").strip()
            if not task:
                break
            tasks.append(task)
        
        if not tasks:
            print("❌ Không có task nào được nhập")
            return
        
        print(f"\n🔄 Xử lý batch {len(tasks)} tasks...")
        responses = self.runner.run_batch(tasks, show_progress=True)
        
        print("\n📊 Kết quả batch:")
        for i, (task, response) in enumerate(zip(tasks, responses), 1):
            print(f"\n{i}. Task: {task}")
            print(f"   Response: {response[:100]}..." if len(response) > 100 else f"   Response: {response}")
    
    def run_demo_mode(self):
        """Run demo mode"""
        print("\n🎮 Chạy Demo Mode...")
        self.runner.run_demo()
    
    def show_info_and_stats(self):
        """Show system info and statistics"""
        print("\n📊 System Information")
        print("=" * 30)
        
        # Factory info
        factory_info = self.factory.get_factory_info()
        print(f"Available Models: {factory_info['available_models']}")
        print(f"Available Tools: {len(factory_info['available_tools'])}")
        print(f"Debug Mode: {factory_info['debug_mode']}")
        
        # Agent info
        if self.agent:
            print(f"\nAgent: {self.agent.name}")
            print(f"Tools: {self.agent.get_available_tools()}")
            
            # Session stats
            stats = self.runner.get_session_stats()
            if stats:
                print(f"\nSession Stats: {stats}")
        
        # Config info
        print(f"\nConfiguration:")
        print(f"- LLM Model: {self.config.get('llm.model')}")
        print(f"- Temperature: {self.config.get('llm.temperature')}")
        print(f"- Max Iterations: {self.config.get('agent.max_iterations')}")
    
    def run(self):
        """Main application loop"""
        try:
            # Show welcome
            self.show_welcome_message()
            
            # Initialize agent
            if not self.initialize_agent():
                return False
            
            print("✅ Agent đã sẵn sàng!\n")
            
            # Main loop
            while True:
                try:
                    choice = self.show_menu()
                    
                    if choice == "0":
                        print("👋 Tạm biệt!")
                        break
                    elif choice == "1":
                        self.run_interactive_mode()
                    elif choice == "2":
                        self.run_single_task_mode()
                    elif choice == "3":
                        self.run_batch_mode()
                    elif choice == "4":
                        self.run_demo_mode()
                    elif choice == "5":
                        self.show_info_and_stats()
                    else:
                        print("❌ Lựa chọn không hợp lệ")
                    
                    # Separator
                    if choice != "0":
                        print("\n" + "="*50 + "\n")
                        
                except KeyboardInterrupt:
                    print("\n👋 Tạm biệt!")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    print(f"❌ Lỗi: {e}")
        
        except Exception as e:
            logger.error(f"Critical error: {e}")
            print(f"❌ Lỗi nghiêm trọng: {e}")
            return False
        
        return True


def main():
    """Entry point function"""
    try:
        app = AIAgentApp()
        success = app.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n👋 Ứng dụng bị dừng bởi người dùng")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Lỗi khởi tạo ứng dụng: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
