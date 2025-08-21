"""
Graph construction and compilation for the Customer Support Agent.
Defines the workflow structure and compiles the LangGraph.
"""
from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import agent_node, agent_node_with_streaming, tool_node, decide_next_step
from config import get_streaming_config
from psycopg import Connection
from langgraph.checkpoint.postgres import PostgresSaver

def create_agent_workflow(db_connection: Connection):
    """
    Create and compile the agent workflow graph.
    
    Args:
        db_connection: PostgreSQL database connection for checkpointing
        
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
    
    # Create the checkpointer with the passed connection
    checkpointer = PostgresSaver(db_connection)
    
    # Setup the database tables
    checkpointer.setup()
    
    # Compile the workflow with checkpointing
    app = workflow.compile(checkpointer=checkpointer)
    
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