"""
Prompts package for the Customer Support Agent.

This package manages all prompt templates and formatting for the agent,
including ReAct prompts, customer support specific prompts, and custom
prompt templates.

The prompts are managed through a centralized system that allows for
easy customization and extension of agent behavior.
"""

from .agent_prompts import (
    get_agent_prompt,
    get_system_prompt,
    get_customer_support_prompt,
    list_available_prompts,
    register_custom_prompt,
    format_agent_variables,
    AgentPrompts,
    PromptConfig
)

__all__ = [
    # Main prompt functions
    'get_agent_prompt',
    'get_system_prompt', 
    'get_customer_support_prompt',
    
    # Prompt management
    'list_available_prompts',
    'register_custom_prompt',
    'format_agent_variables',
    
    # Classes
    'AgentPrompts',
    'PromptConfig'
]