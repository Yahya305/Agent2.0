"""
Provides current date and time information.
"""

from langchain_core.tools import tool
from datetime import datetime
from utils.logger import logger


@tool
def get_date_and_time() -> str:
    """
    Returns the current date and time in a human-readable format.
    Useful when you need to know the current date or time.

    Returns:
        str: The current date and time
    """
    now = datetime.now()
    human_readable = now.strftime("%A, %B %d, %Y, %I:%M %p")
    logger.debug(f"\n--- Fetching Date Time: {human_readable} ---\n")
    return human_readable
