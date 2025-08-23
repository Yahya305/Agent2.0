"""
Main entry point for the Customer Support Agent.
Handles interactive conversation flow and user commands.
"""

from typing import Optional
import sys

# Import our modular components (we'll create these next)
from config.settings import load_config
from agent.workflow import create_agent_workflow
from utils.conversation import (
    display_conversation_history, 
    generate_new_thread_id,
    run_single_interaction
)
from utils.database import initialize_database, cleanup_database
from tools import register_default_tools
from utils.logger import logger


class CustomerSupportAgent:
    """Main agent class that orchestrates the conversation flow."""
    
    def __init__(self):
        """Initialize the agent with configuration and workflow."""
        logger.info("Initializing Customer Support Agent...")
        
        # Load configuration
        load_config()        
        
        # Initialize database
        self.db_connection = initialize_database()

        # Setup and Load tools
        register_default_tools()
        
        # Create the agent workflow
        self.app = create_agent_workflow(self.db_connection)
        
        logger.info("Agent initialized successfully!")
    
    def display_welcome_message(self):
        """Display welcome message and instructions."""
        logger.info("=" * 60)
        logger.info("Welcome to the Customer Support Agent!")
        logger.info("=" * 60)
        logger.info("\nCommands:")
        logger.info("  - Type your question/message to chat")
        logger.info("  - 'quit', 'exit', or 'bye' to end conversation")
        logger.info("  - 'history' to see full conversation history")
        logger.info("  - 'new' to start a new conversation thread")
        logger.info("  - 'help' to see this message again")
        logger.info("-" * 60)
    
    def get_thread_id(self) -> str:
        """Get thread ID from user input or generate new one."""
        thread_input = input("\nEnter thread ID (or press Enter for new conversation): ").strip()
        
        if thread_input:
            logger.info(f"\nUsing thread ID: {thread_input}")
            # Check if thread has history and display it
            has_history = display_conversation_history(thread_input, self.app)
            if has_history:
                logger.info("Continuing from previous conversation...\n")
            else:
                logger.info("No previous history found. Starting fresh conversation...\n")
            return thread_input
        else:
            thread_id = generate_new_thread_id()
            logger.info(f"\nCreated new thread ID: {thread_id}")
            logger.info("Starting new conversation...\n")
            return thread_id
    
    def handle_special_commands(self, user_input: str, thread_id: str) -> tuple[bool, bool, Optional[str]]:
        """
        Handle special commands like quit, history, new, help.
        
        Returns:
            (should_continue, new_thread_id)
        """
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit', 'bye']:
            logger.info("\nGoodbye! Have a great day!")
            return True, False, thread_id
        
        elif command == 'history':
            display_conversation_history(thread_id, self.app)
            return False, False, thread_id
        
        elif command == 'new':
            new_thread_id = generate_new_thread_id()
            logger.info(f"\nStarted new conversation with thread ID: {new_thread_id}")
            return False, False, new_thread_id
        
        elif command == 'help':
            self.display_welcome_message()
            return False, False, thread_id
        
        # Not a special command
        return False, True, thread_id
    
    def conversation_loop(self, thread_id: str):
        """Main conversation loop for a given thread."""
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    logger.info("Please enter a message or command.")
                    continue
                
                # Handle special commands
                end_convo, forward_to_agent, new_thread_id = self.handle_special_commands(user_input, thread_id)
                
                if end_convo:
                    break
                
                # Check if thread ID changed (e.g., 'new' command)
                if new_thread_id != thread_id:
                    thread_id = new_thread_id
                    continue

                if not forward_to_agent:
                    continue
                
                # Regular conversation - run the agent
                success = run_single_interaction(user_input, thread_id, self.app)
                
                if not success:
                    logger.info("Something went wrong. Please try again.")
                    
            except KeyboardInterrupt:
                logger.info("\n\nConversation interrupted. Goodbye!")
                break
            except Exception as e:
                logger.info(f"\nAn unexpected error occurred: {e}")
                logger.info("Please try again.")
    
    def run(self):
        """Main execution method."""
        try:
            self.display_welcome_message()
            thread_id = self.get_thread_id()
            self.conversation_loop(thread_id)
        except KeyboardInterrupt:
            logger.info("\n\nApplication interrupted. Goodbye!")
        except Exception as e:
            logger.info(f"\nA critical error occurred: {e}")
            sys.exit(1)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        cleanup_database(self.db_connection)
        logger.info("Resources cleaned up.")


def main():
    """Entry point of the application."""
    print("Starting Customer Support Agent...")
    agent = CustomerSupportAgent()
    agent.run()


if __name__ == "__main__":
    main()