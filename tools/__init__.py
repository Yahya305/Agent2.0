"""
Tools package for the Customer Support Agent.

This package contains all tools that the agent can use to perform actions
such as web searches, calculations, data retrieval, etc.

The tools are managed through a central registry system that allows for
easy addition, removal, and management of tools.
"""

from .web_search import web_search
from .tool_registry import (
    get_all_tools,
    get_tool_names,
    get_tool,
    register_tool,
    unregister_tool,
    list_available_tools,
    get_tool_info,
    ToolRegistry
)

__all__ = [
    # Individual tools
    'web_search',
    
    # Registry functions
    'get_all_tools',
    'get_tool_names', 
    'get_tool',
    'register_tool',
    'unregister_tool',
    'list_available_tools',
    'get_tool_info',
    'ToolRegistry'
]