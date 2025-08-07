"""
Agent state definition for the Customer Support Agent.
Defines the state structure used throughout the agent workflow.
"""

from typing import List, TypedDict, Annotated, Literal
from operator import add
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """
    State structure for the customer support agent.
    
    Attributes:
        messages: List of conversation messages with automatic message addition
        next_action: Determines the next step in the workflow 
        actions: List of tool actions to be executed
    """
    messages: Annotated[List[BaseMessage], add_messages]
    next_action: Literal["call_tool", "respond"]
    actions: List[dict]