"""
Conversation history and display functions.
Manages conversation threading, history display, and interaction handling.
"""

import uuid
from typing import Optional, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph

from .streaming import stream_response
from agent.state import AgentState
from .logger import logger


def generate_new_thread_id() -> str:
    """
    Generate a new unique thread ID for conversations.
    
    Returns:
        str: Unique thread identifier
    """
    return f"customer_{str(uuid.uuid4())[:8]}"


def display_conversation_history(thread_id: str, app) -> bool:
    """
    Display existing conversation history for a thread.
    
    Args:
        thread_id: Thread identifier to retrieve history for
        app: Compiled LangGraph application
        
    Returns:
        bool: True if history exists and was displayed, False otherwise
    """
    try:
        # Get state from the compiled graph
        state = app.get_state(config={"configurable": {"thread_id": thread_id}})
        
        if state and state.values and "messages" in state.values:
            messages = state.values["messages"]
            
            if messages:
                logger.info("\n--- Conversation History for Thread: {} ---", thread_id)
                display_messages(messages)
                logger.info("--- End of History ---\n")
                return True
            else:
                logger.info("No conversation history found for thread: {}", thread_id)
                return False
        else:
            logger.info("No conversation history found for thread: {}", thread_id)
            return False
            
    except Exception as e:
        logger.debug("Error retrieving conversation history: {}", e)
        return False


def display_messages(messages: List[BaseMessage]) -> None:
    """
    Display a list of messages in a formatted way.
    
    Args:
        messages: List of conversation messages to display
    """
    for i, message in enumerate(messages, 1):
        if isinstance(message, HumanMessage):
            logger.info("{}. User: {}", i, message.content)
        elif isinstance(message, AIMessage):
            logger.info("{}. Agent: {}", i, message.content)
        elif isinstance(message, ToolMessage):
            truncated_content = message.content[:200] + ('...' if len(message.content) > 200 else '')
            logger.info("{}. Tool Output: {}", i, truncated_content)


def get_conversation_summary(messages: List[BaseMessage]) -> Dict[str, Any]:
    """
    Generate a summary of the conversation.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        dict: Conversation summary with statistics
    """
    summary = {
        "total_messages": len(messages),
        "user_messages": 0,
        "agent_messages": 0,
        "tool_messages": 0,
        "first_message_time": None,
        "last_message_time": None,
        "topics_mentioned": []
    }
    
    for message in messages:
        if isinstance(message, HumanMessage):
            summary["user_messages"] += 1
        elif isinstance(message, AIMessage):
            summary["agent_messages"] += 1
        elif isinstance(message, ToolMessage):
            summary["tool_messages"] += 1
    
    return summary


def run_single_interaction(user_input: str, thread_id: str, app: CompiledStateGraph[AgentState, None, AgentState, AgentState]) -> bool:
    """
    Run a single interaction with the agent.
    
    Args:
        user_input: User's message/question
        thread_id: Thread identifier for conversation continuity
        app: Compiled LangGraph application
        
    Returns:
        bool: True if interaction was successful, False otherwise
    """
    logger.info("\n--- User: {} ---", user_input)
    
    # Create initial message and state
    initial_message = HumanMessage(content=user_input)
    initial_state: AgentState = {
        "messages": [initial_message], 
        "next_action": "respond",
        "actions": []
    }
    
    final_response_streamed = False
    
    try:
        # Stream the interaction
        for step in app.stream(
            input=initial_state, 
            config={"configurable": {"thread_id": thread_id}}
        ):
            if "__end__" not in step:
                for node_name, node_output in step.items():
                    # Handle different node outputs
                    if node_name == "agent" and "messages" in node_output:
                        if node_output.get("next_action") == "respond":
                            # This is the final response
                            last_msg = node_output["messages"][-1] if node_output["messages"] else None
                            if last_msg and isinstance(last_msg, AIMessage) and not final_response_streamed:
                                # logger.info("Agent: ", end='', flush=True)
                                # stream_response(last_msg.content)
                                final_response_streamed = True
                                logger.info("")  # New line after response
                        elif node_output.get("next_action") == "call_tool":
                            # Show tool usage indicator
                            logger.info("Agent: [Using tools to help you...]")
                    
                    elif node_name == "tool_node":
                        # Tool execution feedback
                        logger.debug("[Tools executed, processing results...]")
                        
        
        if not final_response_streamed:
            logger.info("Agent: I apologize, but I couldn't generate a response. Please try again.")
        
        return True
        
    except Exception as e:
        logger.debug("\nAn error occurred during interaction: {}", e)
        return False


def export_conversation(thread_id: str, app, format: str = "text") -> Optional[str]:
    """
    Export conversation history in various formats.
    
    Args:
        thread_id: Thread identifier
        app: Compiled LangGraph application  
        format: Export format ("text", "json", "markdown")
        
    Returns:
        str: Formatted conversation data or None if failed
    """
    try:
        state = app.get_state(config={"configurable": {"thread_id": thread_id}})
        
        if not (state and state.values and "messages" in state.values):
            return None
            
        messages = state.values["messages"]
        
        if format.lower() == "json":
            import json
            return json.dumps([
                {
                    "type": type(msg).__name__,
                    "content": msg.content,
                    "timestamp": getattr(msg, 'timestamp', None)
                }
                for msg in messages
            ], indent=2)
            
        elif format.lower() == "markdown":
            md_content = f"# Conversation History - {thread_id}\n\n"
            for i, msg in enumerate(messages, 1):
                if isinstance(msg, HumanMessage):
                    md_content += f"## {i}. User\n{msg.content}\n\n"
                elif isinstance(msg, AIMessage):
                    md_content += f"## {i}. Agent\n{msg.content}\n\n"
                elif isinstance(msg, ToolMessage):
                    md_content += f"## {i}. Tool Output\n```\n{msg.content}\n```\n\n"
            return md_content
            
        else:  # Default to text format
            text_content = f"Conversation History - {thread_id}\n"
            text_content += "=" * 50 + "\n"
            for i, msg in enumerate(messages, 1):
                if isinstance(msg, HumanMessage):
                    text_content += f"{i}. User: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    text_content += f"{i}. Agent: {msg.content}\n"
                elif isinstance(msg, ToolMessage):
                    text_content += f"{i}. Tool: {msg.content}\n"
            return text_content
            
    except Exception as e:
        logger.debug("Error exporting conversation: {}", e)
        return None


def search_conversation_history(thread_id: str, app, search_term: str) -> List[Dict[str, Any]]:
    """
    Search through conversation history for specific terms.
    
    Args:
        thread_id: Thread identifier
        app: Compiled LangGraph application
        search_term: Term to search for
        
    Returns:
        List of matching messages with context
    """
    try:
        state = app.get_state(config={"configurable": {"thread_id": thread_id}})
        
        if not (state and state.values and "messages" in state.values):
            return []
            
        messages = state.values["messages"]
        matches = []
        
        for i, msg in enumerate(messages):
            if search_term.lower() in msg.content.lower():
                matches.append({
                    "index": i,
                    "type": type(msg).__name__,
                    "content": msg.content,
                    "match_context": _get_match_context(msg.content, search_term)
                })
        
        return matches
        
    except Exception as e:
        logger.debug("Error searching conversation history: {}", e)
        return []


def _get_match_context(content: str, search_term: str, context_chars: int = 100) -> str:
    """
    Get context around a search term match.
    
    Args:
        content: Full message content
        search_term: The search term that was matched
        context_chars: Number of characters to include around the match
        
    Returns:
        str: Context snippet around the match
    """
    lower_content = content.lower()
    lower_term = search_term.lower()
    
    match_index = lower_content.find(lower_term)
    if match_index == -1:
        return content[:context_chars] + "..."
    
    start = max(0, match_index - context_chars // 2)
    end = min(len(content), match_index + len(search_term) + context_chars // 2)
    
    context = content[start:end]
    if start > 0:
        context = "..." + context
    if end < len(content):
        context = context + "..."
    
    return context


def get_active_threads(app, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get information about active conversation threads.
    
    Args:
        app: Compiled LangGraph application
        limit: Maximum number of threads to return
        
    Returns:
        List of thread information
    """
    # Note: This is a placeholder as LangGraph doesn't provide a direct way
    # to list all threads. In a production system, you might want to track
    # this separately in your database.
    return []