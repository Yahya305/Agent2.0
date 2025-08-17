"""
Web search tool for the Customer Support Agent.
Provides web search capabilities for finding up-to-date information.
"""

# import os
from langchain_core.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults
# from utils.logger import logger
from config.settings import get_config
from firecrawl import FirecrawlApp
from typing import Dict


# Initialize search tool after ensuring API key is available
@tool
def web_search(query: str) -> Dict:
    """
    Search the web using FireCrawl API
    
    Args:
        query (str): Search query
        limit (int): Maximum number of results to return (default: 5)
    
    Returns:
        Dict: Response in format:
        {
            "success": bool,
            "data": [
                {
                    "title": str,
                    "description": str, 
                    "url": str
                }
            ]
        }
        Or error format:
        {
            "success": false,
            "error": str
        }
    """
    try:
        app = FirecrawlApp(api_key=get_config('firecrawl_api_key'))
        
        response = app.search(
            query=query,
            limit=2
        )
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"FireCrawl search failed: {str(e)}"
        }




# class WebSearchTool:
#     """Web search tool for finding current information and external facts."""

#     @tool
#     def _placeholder_search(self, query: str) -> str:
#         """Placeholder search that returns a default message."""
#         logger.debug("\n--- USING PLACEHOLDER SEARCH FOR: '{}' ---\n", query)
#         return f"To enable real web search, please configure the search tool with set_searcher(). Query was: {query}"

#     def __init__(self):
#         """Initialize the web search tool with placeholder."""
#         try:
#             self.set_searcher()  # Try to initialize with real searcher
#         except Exception as e:
#             logger.debug("Failed to initialize real searcher: {}. Using placeholder.", str(e))
#             self.tool = self._placeholder_search  # Fallback to placeholder
    
#     def get_searcher(self):
#         return self.tool

#     def set_searcher(self):
#         """Configure the real Tavily search implementation."""
#         api_key = get_config('tavily_api_key')
#         logger.debug("Got API key from config: {}", "Found" if api_key else "Not found")

#         if not api_key:
#             logger.debug("Checking environment for API key")
#             api_key = os.getenv('TAVILY_API_KEY')
#             logger.debug("Environment API key: {}", "Found" if api_key else "Not found")
        
#         if not api_key:
#             raise ValueError("Tavily API key not found. Please ensure it is set in constants.py or environment variables.")

#         self.tool = TavilySearchResults(
#             max_results=2,
#             name="tavily_search_results_json",
#             tavily_api_key=api_key
#         )

# web_search = WebSearchTool()


















# def get_web_search_tool():
#     """Get configured web search tool instance."""
#     api_key = get_config('tavily_api_key')
#     print(api_key," API key from config")
#     if not api_key:
#         logger.debug("Tavily API key not found in config, checking environment")
#         api_key = os.getenv('TAVILY_API_KEY')
        
#     if not api_key:
#         raise ValueError("Tavily API key not found. Please ensure it is set in constants.py or environment variables.")
    
#     return TavilySearchResults(
#         max_results=2,
#         name="tavily_search_results_json",
#         tavily_api_key=api_key
#     )

# Initialize the web search tool
# web_search = get_web_search_tool()
# def web_search(query: str) -> str:
#     """
#     Searches the web for the given query and returns relevant information.
#     Useful when you need to find up-to-date information or external facts.
    
#     Args:
#         query: The search query string
        
#     Returns:
#         str: Search results or relevant information
#     """
#     logger.debug(f"\n--- PERFORMING WEB SEARCH FOR: '{query}' ---\n")
    
#     # Simulate web search with predefined responses
#     # In a real implementation, this would connect to a search API
    
#     query_lower = query.lower()
    
#     # Product information queries
#     if "latest iphone" in query_lower or "newest iphone" in query_lower:
#         return "The latest iPhone model as of 2024 is the iPhone 16 series, featuring enhanced AI capabilities, improved cameras, and the new A18 chip."
    
#     elif "iphone 16" in query_lower:
#         return "The iPhone 16 features the A18 Bionic chip, improved camera system with 48MP main camera, Action Button, USB-C connector, and enhanced battery life."
    
#     # Coffee maker queries
#     elif "best coffee maker" in query_lower or "coffee machine" in query_lower:
#         return "Top-rated coffee makers include: AeroPress for manual brewing, Chemex for pour-over, Breville Barista Express for espresso, and Technivorm Moccamaster for drip coffee."
    
#     elif "aeropress" in query_lower:
#         return "AeroPress is a popular manual coffee maker known for producing smooth, rich coffee. It uses pressure brewing and is favored by coffee enthusiasts."
    
#     # Store and business queries  
#     elif "store hours" in query_lower or "opening hours" in query_lower or "business hours" in query_lower:
#         return "Our store is open Monday to Saturday from 9 AM to 7 PM. Closed on Sundays. Holiday hours may vary."
    
#     elif "store location" in query_lower or "address" in query_lower:
#         return "Visit us at 123 Main Street, Downtown. Free parking available. Public transit accessible via Metro Line 2."
    
#     # Product warranty and support
#     elif "warranty" in query_lower:
#         return "Our products come with a 1-year limited warranty covering manufacturing defects. Extended warranty options available at purchase."
    
#     elif "return policy" in query_lower:
#         return "30-day return policy for unused items in original packaging. Refunds processed within 5-7 business days."
    
#     elif "customer support" in query_lower or "contact" in query_lower:
#         return "Customer Support: Phone (555) 123-4567, Email support@company.com, Live Chat available 9 AM - 6 PM weekdays."
    
#     # Technology and product specs
#     elif "android" in query_lower and ("latest" in query_lower or "newest" in query_lower):
#         return "Latest Android smartphones include Samsung Galaxy S24 series, Google Pixel 8 series, and OnePlus 12, featuring Android 14 and AI enhancements."
    
#     elif "laptop" in query_lower and "best" in query_lower:
#         return "Top laptops for 2024: MacBook Air M3 for portability, ThinkPad X1 Carbon for business, Dell XPS 13 for Windows users, and ASUS ROG for gaming."
    
#     # Weather queries
#     elif "weather" in query_lower:
#         return "For current weather conditions, please check your local weather service. General forecast shows seasonal temperatures with occasional precipitation."
    
#     # Shopping and deals
#     elif "sale" in query_lower or "discount" in query_lower or "deal" in query_lower:
#         return "Current promotions: 15% off electronics, Buy-2-Get-1 on accessories, and free shipping on orders over $50. Check our website for latest deals."
    
#     # Shipping information
#     elif "shipping" in query_lower or "delivery" in query_lower:
#         return "Standard shipping: 3-5 business days ($5.99). Express shipping: 1-2 business days ($12.99). Free shipping on orders over $50."
    
#     # Default response for unknown queries
#     else:
#         return f"I searched for '{query}' but couldn't find specific information. Please try rephrasing your query or contact customer support for detailed assistance."


# # Additional specialized search functions (could be separate tools if needed)

# def search_product_info(product_name: str) -> str:
#     """Search for specific product information."""
#     return web_search(f"product information {product_name}")


# def search_support_info(topic: str) -> str:
#     """Search for customer support related information."""
#     return web_search(f"customer support {topic}")


# def search_store_info(info_type: str) -> str:
#     """Search for store-related information."""
#     return web_search(f"store {info_type}")