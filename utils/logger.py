"""
Custom logger implementation for the agent system.
Provides debug and info level logging with configurable debug mode.
"""

class Logger:
    """Custom logger class with debug and info methods."""
    
    def __init__(self, debug_mode: bool = False):
        """Initialize logger with optional debug mode."""
        self._debug_mode = debug_mode

    def info(self, message: str, *args, end: str = '\n', flush: bool = False, **kwargs) -> None:
        """
        Log info message - always displayed.
        
        Args:
            message: The message to log
            *args: Format string arguments
            end: String appended after the message (default: '\n')
            flush: Whether to forcibly flush the stream (default: False)
            **kwargs: Format string keyword arguments
        """
        if args or kwargs:
            message = message.format(*args, **kwargs)
        print(message, end=end, flush=flush)

    def debug(self, message: str, *args, end: str = '\n', flush: bool = False, **kwargs) -> None:
        """
        Log debug message - only displayed if debug mode is enabled.
        
        Args:
            message: The message to log
            *args: Format string arguments
            end: String appended after the message (default: '\n')
            flush: Whether to forcibly flush the stream (default: False)
            **kwargs: Format string keyword arguments
        """
        if not self._debug_mode:
            return
            
        if args or kwargs:
            message = message.format(*args, **kwargs)
        print(message, end=end, flush=flush)

    @property
    def debug_mode(self) -> bool:
        """Get current debug mode state."""
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        """Set debug mode state."""
        self._debug_mode = value


# Create default logger instance
logger = Logger(debug_mode=True)
