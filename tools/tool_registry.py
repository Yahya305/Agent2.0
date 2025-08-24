"""
Tool registry for managing all available tools in the Customer Support Agent.
Provides centralized tool management and easy extension capabilities.
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool

from .web_search import web_search
from .date_time import get_date_and_time
from .city_weather import get_weather
from .memory import create_memory_tools


class ToolRegistry:
    """Central registry for managing all available tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools = {}
        self._tool_descriptions = {}
    
    def register_default_tools(self):
        """Register the default set of tools."""

        memory_tools = create_memory_tools()
        for tool in memory_tools:
            self.register_tool(tool, tool.description)

        # self.get_tool("store_memory").invoke('{"content": "User Saim likes Football", "importance": "medium"}')
        # self.get_tool("retrieve_memory").invoke('{"query": "Yahya Likes Chess", "user_id": "Yahya"}')
        self.register_tool(web_search, "Web search for finding current information and external facts")
        self.register_tool(get_date_and_time, "Provides current date and time information")
        self.register_tool(get_weather, "Provides current weather information in a city")
    
    def register_tool(self, tool: BaseTool, description: str = None):
        """
        Register a new tool in the registry.
        
        Args:
            tool: The tool to register (must be a LangChain tool)
            description: Optional description of the tool's purpose
        """
        tool_name = tool.name
        self._tools[tool_name] = tool
        
        if description:
            self._tool_descriptions[tool_name] = description
        elif hasattr(tool, 'description'):
            self._tool_descriptions[tool_name] = tool.description
        else:
            self._tool_descriptions[tool_name] = f"Tool: {tool_name}"
    
    def unregister_tool(self, tool_name: str):
        """
        Remove a tool from the registry.
        
        Args:
            tool_name: Name of the tool to remove
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            if tool_name in self._tool_descriptions:
                del self._tool_descriptions[tool_name]
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Get a specific tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            The requested tool or None if not found
        """
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all registered tools.
        
        Returns:
            List of all registered tools
        """
        return list(self._tools.values())
    
    def get_tool_names(self) -> List[str]:
        """
        Get names of all registered tools.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_tool_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about all tools.
        
        Returns:
            Dictionary with tool info including name, description, and parameters
        """
        tool_info = {}
        
        for name, tool in self._tools.items():
            tool_info[name] = {
                'name': name,
                'description': self._tool_descriptions.get(name, ''),
                'args_schema': getattr(tool, 'args_schema', None),
                'return_direct': getattr(tool, 'return_direct', False)
            }
        
        return tool_info
    
    def list_tools(self) -> str:
        """
        Get a formatted string listing all available tools.
        
        Returns:
            Formatted string with tool information
        """
        if not self._tools:
            return "No tools registered."
        
        tool_list = ["Available Tools:"]
        for name, description in self._tool_descriptions.items():
            tool_list.append(f"  - {name}: {description}")
        
        return "\n".join(tool_list)
    
    def tool_exists(self, tool_name: str) -> bool:
        """
        Check if a tool exists in the registry.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool exists, False otherwise
        """
        return tool_name in self._tools


# Global tool registry instance
_tool_registry = ToolRegistry()


# Convenience functions for external use
def register_default_tools() -> List[BaseTool]:
    """Registered Default tools."""
    return _tool_registry.register_default_tools()

# Convenience functions for external use
def get_all_tools() -> List[BaseTool]:
    """Get all registered tools."""
    return _tool_registry.get_all_tools()


def get_tool_names() -> List[str]:
    """Get names of all registered tools."""
    return _tool_registry.get_tool_names()


def get_tool(tool_name: str) -> BaseTool:
    """Get a specific tool by name."""
    return _tool_registry.get_tool(tool_name)


def register_tool(tool: BaseTool, description: str = None):
    """Register a new tool."""
    _tool_registry.register_tool(tool, description)


def unregister_tool(tool_name: str):
    """Remove a tool from the registry."""
    _tool_registry.unregister_tool(tool_name)


def list_available_tools() -> str:
    """Get a formatted list of available tools."""
    return _tool_registry.list_tools()


def get_tool_info() -> Dict[str, Dict[str, Any]]:
    """Get detailed information about all tools."""
    return _tool_registry.get_tool_info()

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    """
    Execute a tool with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments to pass to the tool
        
    Returns:
        The output from the executed tool
    """
    tool = _tool_registry.get_tool(tool_name)
    
    if not tool:
        raise ValueError(f"Tool '{tool_name}' not found in registry.")
    
    return tool.invoke(tool_args)
