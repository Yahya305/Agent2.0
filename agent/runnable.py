"""
Agent runnable chain setup for the Customer Support Agent.
Handles the creation and configuration of the agent's runnable chain.
"""

from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub

from tools.tool_registry import get_all_tools
from config.settings import get_model_config


def get_chat_history(messages: List[BaseMessage]) -> List[BaseMessage]:
    """
    Extract chat history from all messages, excluding the last user message.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        List of messages excluding the last user message
    """
    if not messages:
        return []
    return messages[:-1]


def get_current_input(messages: List[BaseMessage]) -> str:
    """
    Extract the content of the last HumanMessage as the current input.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Content of the last human message
    """
    if messages and isinstance(messages[-1], HumanMessage):
        return messages[-1].content
    return ""


def get_agent_scratchpad(messages: List[BaseMessage]) -> List[BaseMessage]:
    """
    Extracts tool calls and tool outputs to form the agent_scratchpad.
    This is critical for ReAct to function properly.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        List of AI and Tool messages for the scratchpad
    """
    scratchpad = []
    for msg in messages:
        if isinstance(msg, AIMessage):
            scratchpad.append(msg)
        elif isinstance(msg, ToolMessage):
            scratchpad.append(msg)
    return scratchpad


def get_agent_prompt():
    """
    Get the agent prompt template from LangChain Hub.
    
    Returns:
        ChatPromptTemplate for the ReAct agent
    """
    return hub.pull("hwchase17/react-chat")


def get_llm_with_tools():
    """
    Initialize and configure the LLM with tools.
    
    Returns:
        Configured LLM instance with bound tools
    """
    model_config = get_model_config()
    tools = get_all_tools()
    
    llm = ChatGoogleGenerativeAI(
        model=model_config["name"],
        temperature=model_config["temperature"],
    ).bind_tools(tools)
    
    return llm


def get_agent_runnable():
    """
    Create and return the complete agent runnable chain.
    
    Returns:
        Configured runnable chain for the agent
    """
    tools = get_all_tools()
    agent_prompt = get_agent_prompt()
    llm_with_tools = get_llm_with_tools()
    
    agent_runnable = (
        RunnablePassthrough.assign(
            tools=lambda x: tools,
            tool_names=lambda x: [t.name for t in tools],
            input=lambda x: get_current_input(x["messages"]),
            chat_history=lambda x: get_chat_history(x["messages"]),
            agent_scratchpad=lambda x: get_agent_scratchpad(x["messages"])
        )
        | agent_prompt
        | llm_with_tools
    )
    
    return agent_runnable