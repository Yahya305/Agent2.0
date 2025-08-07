"""
Configuration package for the Customer Support Agent.

This package handles all configuration management including:
- Environment variables and API keys
- Application settings
- Model configuration
- Database settings
- Streaming preferences
"""

from .settings import (
    load_config,
    get_config,
    update_config,
    get_model_config,
    get_database_config,
    get_streaming_config,
    get_agent_config,
    is_streaming_enabled,
    is_real_time_streaming
)

from .constants import (
    GOOGLE_API_KEY,
    LANGSMITH_TRACING,
    LANGSMITH_ENDPOINT,
    LANGSMITH_API_KEY,
    LANGSMITH_PROJECT
)

__all__ = [
    # Settings functions
    'load_config',
    'get_config',
    'update_config',
    'get_model_config',
    'get_database_config',
    'get_streaming_config',
    'get_agent_config',
    'is_streaming_enabled',
    'is_real_time_streaming',
    
    # Constants
    'GOOGLE_API_KEY',
    'LANGSMITH_TRACING',
    'LANGSMITH_ENDPOINT',
    'LANGSMITH_API_KEY',
    'LANGSMITH_PROJECT',
]