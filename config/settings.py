"""
Configuration management for the Customer Support Agent.
Handles environment variables, API keys, and application settings.
"""

import os
from pathlib import Path
from typing import Dict, Any


# Configuration dictionary to hold all settings
CONFIG = {}


def load_api_keys():
    """Load API keys from constants file or environment."""
    try:
        from config.constants import (
            api_key,
            GOOGLE_API_KEY, 
            LANGSMITH_API_KEY,
            LANGSMITH_TRACING,
            LANGSMITH_ENDPOINT,
            LANGSMITH_PROJECT,
            FIRECRAWL_API_KEY
        )
        
        # Set environment variables if not already set
        if not os.environ.get("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
            
        if not os.environ.get("LANGSMITH_API_KEY"):
            os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY

        if not os.environ.get("FIRECRAWL_API_KEY"):
            os.environ["FIRECRAWL_API_KEY"] = FIRECRAWL_API_KEY
            
        # Store in config
        CONFIG['api_key'] = api_key
        CONFIG['google_api_key'] = GOOGLE_API_KEY
        CONFIG['langsmith_api_key'] = LANGSMITH_API_KEY
        CONFIG['langsmith_tracing'] = LANGSMITH_TRACING
        CONFIG['langsmith_endpoint'] = LANGSMITH_ENDPOINT
        CONFIG['langsmith_project'] = LANGSMITH_PROJECT
        CONFIG['firecrawl_api_key'] = FIRECRAWL_API_KEY
        
    except ImportError:
        print("Warning: constants.py not found. Make sure API keys are set in environment variables.")
        CONFIG['api_key'] = os.environ.get("OPENAI_API_KEY")
        CONFIG['google_api_key'] = os.environ.get("GOOGLE_API_KEY")
        CONFIG['langsmith_api_key'] = os.environ.get("LANGSMITH_API_KEY")
        CONFIG['langsmith_tracing'] = os.environ.get("LANGSMITH_TRACING", "true")
        CONFIG['langsmith_endpoint'] = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        CONFIG['langsmith_project'] = os.environ.get("LANGSMITH_PROJECT", "FirstApp")
        CONFIG['firecrawl_api_key'] = os.environ.get("FIRECRAWL_API_KEY")


def setup_langsmith():
    """Configure LangSmith tracing and monitoring."""
    # Use values from constants.py or fallback to defaults
    langsmith_config = {
        "LANGCHAIN_TRACING_V2": CONFIG.get('langsmith_tracing', 'true'),
        "LANGCHAIN_ENDPOINT": CONFIG.get('langsmith_endpoint', 'https://api.smith.langchain.com'),
        "LANGCHAIN_PROJECT": CONFIG.get('langsmith_project', 'FirstApp')
    }
    
    for key, value in langsmith_config.items():
        if not os.environ.get(key):
            os.environ[key] = value
    
    # Use LANGSMITH_API_KEY for LANGCHAIN_API_KEY if not set
    if not os.environ.get("LANGCHAIN_API_KEY") and CONFIG.get('langsmith_api_key'):
        os.environ["LANGCHAIN_API_KEY"] = CONFIG['langsmith_api_key']
    
    CONFIG['langsmith'] = langsmith_config


def setup_model_config():
    """Configure LLM model settings."""
    CONFIG['model'] = {
        'name': 'gemini-2.0-flash',
        'temperature': 0.7,
        'max_tokens': None,  # Use model default
        'timeout': 60  # seconds
    }


def setup_streaming_config():
    """Configure streaming behavior."""
    CONFIG['streaming'] = {
        'enabled': True,  # Enable streaming by default
        'real_time': True,  # True for real-time LLM streaming, False for simulated
        'delay': 0.03,  # Delay between words for simulated streaming
        'show_tool_indicator': True  # Show "[Using tools...]" indicator
    }


def setup_database_config():
    """Configure database settings."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    CONFIG['database'] = {
        'path': str(data_dir / "customer_support.db"),
        'check_same_thread': False,
        'timeout': 30.0
    }


def setup_agent_config():
    """Configure agent behavior settings."""
    CONFIG['agent'] = {
        'prompt_hub_name': "hwchase17/react-chat",  # LangChain Hub prompt
        'max_iterations': 10,  # Max tool call iterations
        'max_execution_time': 300,  # Max execution time in seconds
        'verbose': True  # Enable verbose logging
    }


def setup_conversation_config():
    """Configure conversation management settings."""
    CONFIG['conversation'] = {
        'max_history_length': 50,  # Max messages to keep in history
        'thread_id_prefix': "customer_",
        'thread_id_length': 8,  # Length of random part of thread ID
        'auto_save': True,  # Auto-save conversation state
        'display_timestamps': False  # Show timestamps in conversation history
    }


def validate_config():
    """Validate that all required configuration is present."""
    required_keys = [
        'google_api_key',
        'model',
        'database',
        'agent',
        'streaming'
    ]
    
    missing_keys = []
    for key in required_keys:
        if key not in CONFIG:
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    # Validate API key is actually set
    if not CONFIG.get('google_api_key'):
        raise ValueError("Google API key is required but not found in constants.py or environment variables")


def get_config(key: str = None) -> Any:
    """
    Get configuration value(s).
    
    Args:
        key: Specific config key to retrieve. If None, returns entire config.
        
    Returns:
        Configuration value or entire config dict.
    """
    if key:
        return CONFIG.get(key)
    return CONFIG


def update_config(key: str, value: Any):
    """Update a configuration value."""
    CONFIG[key] = value


def load_config():
    """Load all configuration settings."""
    print("Loading configuration...")
    
    # Load all configuration sections
    load_api_keys()
    setup_langsmith()
    setup_model_config()
    setup_streaming_config()
    setup_database_config()
    setup_agent_config()
    setup_conversation_config()
    
    # Validate configuration
    validate_config()
    
    print("Configuration loaded successfully!")
    
    # Print some key config info (without sensitive data)
    print(f"Model: {CONFIG['model']['name']}")
    print(f"Database: {CONFIG['database']['path']}")
    print(f"Streaming: {'Enabled' if CONFIG['streaming']['enabled'] else 'Disabled'}")
    print(f"Real-time streaming: {'Yes' if CONFIG['streaming']['real_time'] else 'No (simulated)'}")


# Export commonly used config getters
def get_model_config() -> Dict[str, Any]:
    """Get model configuration."""
    return CONFIG.get('model', {})


def get_database_config() -> Dict[str, Any]:
    """Get database configuration.""" 
    return CONFIG.get('database', {})


def get_streaming_config() -> Dict[str, Any]:
    """Get streaming configuration."""
    return CONFIG.get('streaming', {})


def get_agent_config() -> Dict[str, Any]:
    """Get agent configuration."""
    return CONFIG.get('agent', {})


def is_streaming_enabled() -> bool:
    """Check if streaming is enabled."""
    return CONFIG.get('streaming', {}).get('enabled', False)


def is_real_time_streaming() -> bool:
    """Check if real-time streaming is enabled."""
    streaming_config = CONFIG.get('streaming', {})
    return streaming_config.get('enabled', False) and streaming_config.get('real_time', False)