import re
from utils.logger import logger

def extract_final_answer(content: str) -> str:
    """
    Extract the final answer from ReAct format response.
    
    Args:
        content: The full response content from the agent
        
    Returns:
        str: Clean final answer without the thought process
    """
    # Look for "Final Answer:" pattern
    final_answer_match = re.search(r"Final Answer:\s*(.+)", content, re.DOTALL)
    logger.debug(f"Final answer match: {final_answer_match.group(1)}")
    if final_answer_match:
        return final_answer_match.group(1).strip()
    
    # If no "Final Answer:" found, check if it's a direct response
    # Remove any markdown code blocks and thought patterns
    cleaned_content = re.sub(r"```[\s\S]*?```", "", content)  # Remove code blocks
    cleaned_content = re.sub(r"Thought:.*?(?=Final Answer:|$)", "", cleaned_content, flags=re.DOTALL)
    
    return cleaned_content.strip()
