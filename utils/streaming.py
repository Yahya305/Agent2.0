"""
Streaming utilities for real-time response display.
Handles different types of streaming output for better user experience.
"""

import time
from typing import Optional, Iterator, Any, Callable
from config.settings import get_streaming_config
from langchain.schema import BaseMessage, PromptValue, AIMessage
from langchain.schema.runnable import Runnable
from utils.logger import logger
from typing import Sequence, Any
from utils.response_extractor import extract_final_answer


def stream_response2(llm_with_tools:Runnable[PromptValue | str | Sequence[BaseMessage | list[str] | tuple[str, str] | str | dict[str, Any]], BaseMessage], formatted_prompt) -> None:
    found_final_answer = False
    buffer = ""
    streamed_content = ""
    for chunk in llm_with_tools.stream(formatted_prompt):
        if chunk.content:
            # print(chunk.content, end='', flush=True)
            streamed_content += chunk.content
            buffer += chunk.content
            # Check if we've hit "Final Answer:" and haven't started streaming yet
            if not found_final_answer and "Final Answer:" in buffer:
                found_final_answer = True
                # Find the position after "Final Answer:"
                final_answer_pos = buffer.find("Final Answer:") + len("Final Answer:")
                # Get content after "Final Answer:" and stream it
                after_final_answer = buffer[final_answer_pos:].strip()
                if after_final_answer:
                    print(after_final_answer, end='', flush=True)
                    # ai_message = AIMessage(content=after_final_answer)
            
            # If we're already streaming, display new tokens
            elif found_final_answer:
                print(chunk.content, end='', flush=True)

    if found_final_answer:
        clean_answer = extract_final_answer(streamed_content)
        ai_message = AIMessage(content=clean_answer)
        return ai_message

def stream_response(content: str, delay: Optional[float] = None) -> None:
    """
    Stream text content token by token to simulate real-time response.
    
    Args:
        content: Text content to stream
        delay: Delay between tokens (uses config default if None)
    """
    streaming_config = get_streaming_config()
    
    if delay is None:
        delay = streaming_config.get("delay", 0.03)
    
    # Choose streaming method based on configuration
    stream_method = streaming_config.get("method", "word")
    
    if stream_method == "char":
        _stream_by_character(content, delay)
    elif stream_method == "word":
        _stream_by_word(content, delay)
    elif stream_method == "sentence":
        _stream_by_sentence(content, delay)
    else:
        # Fallback to immediate display
        print(content, end='', flush=True)


def _stream_by_character(content: str, delay: float) -> None:
    """Stream content character by character."""
    for char in content:
        print(char, end='', flush=True)
        time.sleep(delay)


def _stream_by_word(content: str, delay: float) -> None:
    """Stream content word by word."""
    words = content.split(' ')
    
    for i, word in enumerate(words):
        print(word, end='', flush=True)
        if i < len(words) - 1:  # Don't add space after the last word
            print(' ', end='', flush=True)
        time.sleep(delay)


def _stream_by_sentence(content: str, delay: float) -> None:
    """Stream content sentence by sentence."""
    import re
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', content)
    
    for i, sentence in enumerate(sentences):
        if sentence.strip():  # Skip empty sentences
            print(sentence.strip(), end='', flush=True)
            if i < len(sentences) - 1:
                print('.', end='', flush=True)  # Add back the period
            time.sleep(delay * 3)  # Longer delay between sentences


def stream_with_typing_effect(content: str, wpm: int = 200) -> None:
    """
    Stream content with a typing effect based on words per minute.
    
    Args:
        content: Text content to stream
        wpm: Words per minute typing speed
    """
    words = content.split()
    delay_per_word = 60.0 / wpm  # Convert WPM to delay between words
    
    for i, word in enumerate(words):
        print(word, end='', flush=True)
        if i < len(words) - 1:
            print(' ', end='', flush=True)
        time.sleep(delay_per_word)


def stream_with_progress(content: str, show_progress: bool = True) -> None:
    """
    Stream content while showing progress indicator.
    
    Args:
        content: Text content to stream
        show_progress: Whether to show progress indicator
    """
    if not show_progress:
        stream_response(content)
        return
    
    words = content.split()
    total_words = len(words)
    
    for i, word in enumerate(words):
        # Clear previous progress and show current
        if show_progress and i > 0:
            # Move cursor back and clear line
            print('\r', end='')
            print(' ' * 50, end='')  # Clear previous progress
            print('\r', end='')
        
        # Show current word
        print(word, end=' ', flush=True)
        
        # Show progress
        if show_progress:
            progress = int((i + 1) / total_words * 20)  # 20 character progress bar
            bar = '█' * progress + '░' * (20 - progress)
            print(f' [{bar}] {i+1}/{total_words}', end='', flush=True)
        
        time.sleep(0.05)
    
    # Clear progress indicator at the end
    if show_progress:
        print('\r', end='')
        print(' ' * 50, end='')
        print('\r', end='')
        print(content)  # Print final content clean


def create_stream_generator(content: str, chunk_size: int = 10) -> Iterator[str]:
    """
    Create a generator that yields content in chunks for streaming.
    
    Args:
        content: Text content to stream
        chunk_size: Number of characters per chunk
        
    Yields:
        str: Content chunks
    """
    for i in range(0, len(content), chunk_size):
        yield content[i:i + chunk_size]


def stream_with_callback(
    content: str, 
    callback: Callable[[str, int, int], None],
    delay: float = 0.03
) -> None:
    """
    Stream content with a callback function for each chunk.
    
    Args:
        content: Text content to stream
        callback: Function called with (chunk, position, total_length)
        delay: Delay between chunks
    """
    words = content.split()
    total_length = len(content)
    current_position = 0
    
    for word in words:
        # Call callback with current chunk info
        callback(word, current_position, total_length)
        
        print(word, end=' ', flush=True)
        current_position += len(word) + 1
        time.sleep(delay)


def stream_json_response(data: Any, delay: float = 0.02) -> None:
    """
    Stream JSON data in a formatted way.
    
    Args:
        data: Data to stream as JSON
        delay: Delay between characters
    """
    import json
    
    try:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        _stream_by_character(json_str, delay)
    except Exception as e:
        print(f"Error streaming JSON: {e}")
        print(str(data))


def stream_with_highlights(content: str, highlights: list, delay: float = 0.03) -> None:
    """
    Stream content with specific words/phrases highlighted.
    
    Args:
        content: Text content to stream
        highlights: List of words/phrases to highlight
        delay: Delay between words
    """
    words = content.split()
    
    for word in words:
        # Check if word should be highlighted
        should_highlight = any(highlight.lower() in word.lower() for highlight in highlights)
        
        if should_highlight:
            # Use ANSI codes for highlighting (yellow background)
            print(f'\033[43m{word}\033[0m', end=' ', flush=True)
        else:
            print(word, end=' ', flush=True)
        
        time.sleep(delay)


def simulate_thinking_delay(min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
    """
    Simulate thinking/processing time with a visual indicator.
    
    Args:
        min_seconds: Minimum thinking time
        max_seconds: Maximum thinking time
    """
    import random
    
    thinking_time = random.uniform(min_seconds, max_seconds)
    dots = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    start_time = time.time()
    dot_index = 0
    
    print("Thinking ", end='', flush=True)
    
    while time.time() - start_time < thinking_time:
        print(f'\r{dots[dot_index % len(dots)]} Thinking...', end='', flush=True)
        dot_index += 1
        time.sleep(0.1)
    
    print('\r' + ' ' * 20 + '\r', end='', flush=True)  # Clear the thinking indicator


def stream_error_message(error: str, delay: float = 0.05) -> None:
    """
    Stream error messages with appropriate formatting.
    
    Args:
        error: Error message to stream
        delay: Delay between characters
    """
    # Use ANSI codes for red text
    error_formatted = f'\033[31mError: {error}\033[0m'
    _stream_by_character(error_formatted, delay)
    print()  # New line after error


def stream_system_message(message: str, delay: float = 0.02) -> None:
    """
    Stream system messages with appropriate formatting.
    
    Args:
        message: System message to stream
        delay: Delay between characters
    """
    # Use ANSI codes for blue text
    system_formatted = f'\033[34m[System]: {message}\033[0m'
    _stream_by_character(system_formatted, delay)
    print()  # New line after message


def get_streaming_stats() -> dict:
    """
    Get statistics about streaming performance.
    
    Returns:
        dict: Streaming statistics
    """
    config = get_streaming_config()
    
    return {
        "enabled": config.get("enabled", True),
        "method": config.get("method", "word"),
        "delay": config.get("delay", 0.03),
        "supported_methods": ["char", "word", "sentence"],
        "features": [
            "progress_indicator",
            "typing_effect", 
            "json_streaming",
            "highlighting",
            "thinking_simulation"
        ]
    }