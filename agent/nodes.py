"""
Node implementations for the Customer Support Agent workflow.
Contains all the graph nodes including agent_node, tool_node, and their variants.
"""

import re
from typing import Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

from .state import AgentState
from .runnable import get_agent_runnable
from tools.tool_registry import get_all_tools


def parse_action_from_response(content: str) -> dict:
    """
    Parses content string from AIMessage into action data if present.
    
    Args:
        content: The content string from an AI message
        
    Returns:
        dict: Action information if found, None otherwise
    """
    action_match = re.search(r"Action:\s*(.+)", content)
    input_match = re.search(r"Action Input:\s*(.+)", content)
    
    if action_match and input_match:
        return {
            "action": action_match.group(1).strip(),
            "action_input": input_match.group(1).strip()
        }
    return None


def agent_node(state: AgentState) -> AgentState:
    """
    Standard agent node that processes user input and decides next action.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with next action decision
    """
    agent_runnable = get_agent_runnable()
    response = agent_runnable.invoke(state)
    
    # Try to parse action info from response content
    action_info = parse_action_from_response(response.content)
    
    if action_info:
        print("\n--- AGENT DECIDED TO CALL A TOOL ---")
        return {
            "messages": [response],
            "next_action": "call_tool",
            "actions": [action_info]
        }
    else:
        print("\n--- AGENT DECIDED TO RESPOND DIRECTLY ---")
        return {
            "messages": [response],
            "next_action": "respond"
        }


def agent_node_with_streaming(state: AgentState) -> AgentState:
    """
    Agent node that streams the final response in real-time.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with streamed response
    """
    from .runnable import get_llm_with_tools, get_agent_prompt
    from .runnable import get_chat_history, get_current_input, get_agent_scratchpad
    
    agent_runnable = get_agent_runnable()
    tools = get_all_tools()
    
    # Check if this should be a final response (no tool calls needed)
    temp_response = agent_runnable.invoke(state)
    # print("=========================================== TEMP RESPONSE ===========================================\n",temp_response.content,"----",state,"\n===================")
    # print("hererere")
    action_info = parse_action_from_response(temp_response.content)
    
    if action_info:
        # Tool call needed - no streaming, just return normally
        print("\n--- AGENT DECIDED TO CALL A TOOL ---")
        return {
            "messages": [temp_response],
            "next_action": "call_tool", 
            "actions": [action_info]
        }
    else:
        # Final response - stream it!
        print("\n--- AGENT RESPONDING (STREAMING) ---")
        print("Agent: ", end='', flush=True)
        
        # Stream the response in real-time
        streamed_content = ""
        try:
            # Create the enhanced state for streaming
            enhanced_state = {
                "messages": state["messages"],
                "tools": tools,
                "tool_names": [t.name for t in tools],
                "input": get_current_input(state["messages"]),
                "chat_history": get_chat_history(state["messages"]),
                "agent_scratchpad": get_agent_scratchpad(state["messages"])
            }
            
            # Format with the prompt
            agent_prompt = get_agent_prompt()
            formatted_prompt = agent_prompt.invoke(enhanced_state)
            
            # Stream from the LLM
            llm_with_tools = get_llm_with_tools()
            for chunk in llm_with_tools.stream(formatted_prompt):
                if chunk.content:
                    print(chunk.content, end='', flush=True)
                    streamed_content += chunk.content
            
            print()  # New line after streaming
            
            # Create the AI message with the complete streamed content
            ai_message = AIMessage(content=streamed_content)
            
        except Exception as e:
            print(f"\nStreaming error: {e}")
            # Fallback to the temp_response
            ai_message = temp_response
        
        return {
            "messages": [ai_message],
            "next_action": "respond"
        }


def tool_node(state: AgentState) -> AgentState:
    """
    Tool execution node that processes tool calls and returns results.
    
    Args:
        state: Current agent state with tool actions to execute
        
    Returns:
        Updated agent state with tool outputs
    """
    from tools.tool_registry import execute_tool
    
    messages = state["messages"]
    actions = state["actions"]
    last_message = messages[-1] if messages else None
    
    print("Processing tool calls:", actions)
    
    tool_outputs = []
    for action_info in actions:
        print(f"\n--- PROCESSING TOOL CALL: {action_info} ---")
        
        if isinstance(action_info, dict):
            tool_name = action_info.get("action")
            tool_args = action_info.get("action_input")
        else:
            tool_name = getattr(action_info, "action", None)
            tool_args = getattr(action_info, "action_input", None)
            
        if not tool_name or not tool_args:
            print(f"ERROR: Malformed tool call item: {action_info}")
            tool_outputs.append(
                ToolMessage(
                    content="Error: Malformed tool call received.", 
                    tool_call_id=str(tool_name) if tool_name else "unknown"
                )
            )
            continue
            
        # Execute the tool
        try:
            output = execute_tool(tool_name, tool_args)
            print(f"Output from {tool_name}: {output}")
            tool_outputs.append(
                ToolMessage(
                    content=output, 
                    tool_call_id=tool_name
                )
            )
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")
            tool_outputs.append(
                ToolMessage(
                    content=f"Error: Failed to execute tool {tool_name}: {str(e)}", 
                    tool_call_id=tool_name
                )
            )
            
    return {
        "messages": tool_outputs, 
        "next_action": "respond"
    }


def decide_next_step(state: AgentState) -> Literal["tool_node", "respond_and_end"]:
    """
    Decision function to determine the next step in the workflow.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute in the workflow
    """
    if state["next_action"] == "call_tool":
        print("\n--- DECIDING NEXT STEP: CALL TOOL ---")
        return "tool_node"
    elif state["next_action"] == "respond":
        return "respond_and_end"
    else:
        return "respond_and_end"