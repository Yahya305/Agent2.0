"""
Web search tool for the Customer Support Agent.
Provides web search capabilities for finding up-to-date information.
"""

from langchain_core.tools import tool
from utils.logger import logger


@tool
def web_search(query: str) -> str:
    """
    Searches the web for the given query and returns relevant information.
    Useful when you need to find up-to-date information or external facts.
    
    Args:
        query: The search query string
        
    Returns:
        str: Search results or relevant information
    """
    logger.debug(f"\n--- PERFORMING WEB SEARCH FOR: '{query}' ---\n")
    
    # Simulate web search with predefined responses
    # In a real implementation, this would connect to a search API
    
    query_lower = query.lower()
    
    # Product information queries
    if "latest iphone" in query_lower or "newest iphone" in query_lower:
        return "The latest iPhone model as of 2024 is the iPhone 16 series, featuring enhanced AI capabilities, improved cameras, and the new A18 chip."
    
    elif "iphone 16" in query_lower:
        return "The iPhone 16 features the A18 Bionic chip, improved camera system with 48MP main camera, Action Button, USB-C connector, and enhanced battery life."
    
    # Coffee maker queries
    elif "best coffee maker" in query_lower or "coffee machine" in query_lower:
        return "Top-rated coffee makers include: AeroPress for manual brewing, Chemex for pour-over, Breville Barista Express for espresso, and Technivorm Moccamaster for drip coffee."
    
    elif "aeropress" in query_lower:
        return "AeroPress is a popular manual coffee maker known for producing smooth, rich coffee. It uses pressure brewing and is favored by coffee enthusiasts."
    
    # Store and business queries  
    elif "store hours" in query_lower or "opening hours" in query_lower or "business hours" in query_lower:
        return "Our store is open Monday to Saturday from 9 AM to 7 PM. Closed on Sundays. Holiday hours may vary."
    
    elif "store location" in query_lower or "address" in query_lower:
        return "Visit us at 123 Main Street, Downtown. Free parking available. Public transit accessible via Metro Line 2."
    
    # Product warranty and support
    elif "warranty" in query_lower:
        return "Our products come with a 1-year limited warranty covering manufacturing defects. Extended warranty options available at purchase."
    
    elif "return policy" in query_lower:
        return "30-day return policy for unused items in original packaging. Refunds processed within 5-7 business days."
    
    elif "customer support" in query_lower or "contact" in query_lower:
        return "Customer Support: Phone (555) 123-4567, Email support@company.com, Live Chat available 9 AM - 6 PM weekdays."
    
    # Technology and product specs
    elif "android" in query_lower and ("latest" in query_lower or "newest" in query_lower):
        return "Latest Android smartphones include Samsung Galaxy S24 series, Google Pixel 8 series, and OnePlus 12, featuring Android 14 and AI enhancements."
    
    elif "laptop" in query_lower and "best" in query_lower:
        return "Top laptops for 2024: MacBook Air M3 for portability, ThinkPad X1 Carbon for business, Dell XPS 13 for Windows users, and ASUS ROG for gaming."
    
    # Weather queries
    elif "weather" in query_lower:
        return "For current weather conditions, please check your local weather service. General forecast shows seasonal temperatures with occasional precipitation."
    
    # Shopping and deals
    elif "sale" in query_lower or "discount" in query_lower or "deal" in query_lower:
        return "Current promotions: 15% off electronics, Buy-2-Get-1 on accessories, and free shipping on orders over $50. Check our website for latest deals."
    
    # Shipping information
    elif "shipping" in query_lower or "delivery" in query_lower:
        return "Standard shipping: 3-5 business days ($5.99). Express shipping: 1-2 business days ($12.99). Free shipping on orders over $50."
    
    # Default response for unknown queries
    else:
        return f"I searched for '{query}' but couldn't find specific information. Please try rephrasing your query or contact customer support for detailed assistance."


# Additional specialized search functions (could be separate tools if needed)

def search_product_info(product_name: str) -> str:
    """Search for specific product information."""
    return web_search(f"product information {product_name}")


def search_support_info(topic: str) -> str:
    """Search for customer support related information."""
    return web_search(f"customer support {topic}")


def search_store_info(info_type: str) -> str:
    """Search for store-related information."""
    return web_search(f"store {info_type}")