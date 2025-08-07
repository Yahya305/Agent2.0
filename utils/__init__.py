"""
Utils package initialization.
Exposes utility functions for database, conversation, and streaming operations.
"""

# Database utilities
from .database import (
    initialize_database,
    cleanup_database,
    get_database_info,
    vacuum_database,
    backup_database,
    restore_database,
    check_database_health
)

# Conversation utilities
from .conversation import (
    generate_new_thread_id,
    display_conversation_history,
    display_messages,
    get_conversation_summary,
    run_single_interaction,
    export_conversation,
    search_conversation_history,
    get_active_threads
)

# Streaming utilities
from .streaming import (
    stream_response,
    stream_with_typing_effect,
    stream_with_progress,
    create_stream_generator,
    stream_with_callback,
    stream_json_response,
    stream_with_highlights,
    simulate_thinking_delay,
    stream_error_message,
    stream_system_message,
    get_streaming_stats
)

__all__ = [
    # Database
    "initialize_database",
    "cleanup_database", 
    "get_database_info",
    "vacuum_database",
    "backup_database",
    "restore_database",
    "check_database_health",
    
    # Conversation
    "generate_new_thread_id",
    "display_conversation_history",
    "display_messages",
    "get_conversation_summary", 
    "run_single_interaction",
    "export_conversation",
    "search_conversation_history",
    "get_active_threads",
    
    # Streaming
    "stream_response",
    "stream_with_typing_effect",
    "stream_with_progress",
    "create_stream_generator",
    "stream_with_callback",
    "stream_json_response", 
    "stream_with_highlights",
    "simulate_thinking_delay",
    "stream_error_message",
    "stream_system_message",
    "get_streaming_stats"
]