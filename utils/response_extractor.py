import re
from utils.logger import logger

def extract_final_answer(content: str) -> str:
    """
    Extract the final answer from ReAct format response.
    Since we already know "Final Answer:" exists, just extract and clean it.
    
    Args:
        content: The full response content from the agent
        
    Returns:
        str: Clean final answer without the thought process
    """
    # Find the position after "Final Answer:"
    final_answer_pos = content.find("Final Answer:") + len("Final Answer:")
    
    # Extract everything after "Final Answer:"
    answer = content[final_answer_pos:].strip()
    
    # Remove trailing backticks and cleanup
    answer = re.sub(r'```\s*$', '', answer).strip()
    
    logger.debug(f"Extracted final answer: {answer}")
    return answer