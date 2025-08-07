"""
Graph construction and compilation for the Customer Support Agent.
Defines the workflow structure and compiles the LangGraph.
"""

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import agent_node, agent_node_with_streaming, tool_node, decide_next_step
from config.settings import get_streaming_config


def create_agent_workflow(db_connection: sqlite3.Connection):
    """
    Create and compile the agent workflow graph.
    
    Args:
        db_connection: SQLite database connection for checkpointing
        
    Returns:
        Compiled LangGraph application
    """
    # Get streaming configuration
    streaming_config = get_streaming_config()
    use_streaming = streaming_config.get("enabled", True)
    
    # Create the workflow
    workflow = StateGraph(AgentState)
    
    # Choose which agent node to use based on streaming preference
    if use_streaming:
        workflow.add_node("agent", agent_node_with_streaming)
        print("Using streaming agent node")
    else:
        workflow.add_node("agent", agent_node)
        print("Using standard agent node")
    
    # Add tool node
    workflow.add_node("tool_node", tool_node)
    
    # Define the workflow edges
    workflow.add_edge(START, "agent")
    
    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        decide_next_step,
        {
            "tool_node": "tool_node",
            "respond_and_end": END
        }
    )
    
    # Tool node always goes back to agent
    workflow.add_edge("tool_node", "agent")
    
    # Set up checkpointing with SQLite
    sqlite_saver = SqliteSaver(db_connection)
    
    # Compile the graph
    app = workflow.compile(checkpointer=sqlite_saver)
    
    print("Agent workflow compiled successfully!")
    return app


def get_workflow_visualization(app):
    """
    Get a visualization of the workflow graph (if mermaid is available).
    
    Args:
        app: Compiled LangGraph application
        
    Returns:
        Mermaid diagram string or None if not available
    """
    try:
        return app.get_graph().draw_mermaid()
    except Exception as e:
        print(f"Could not generate workflow visualization: {e}")
        return None