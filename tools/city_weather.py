import random
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """
    Retrieves the current weather for a given city.
    
    Args:
        city (str): The name of the city to get the weather for.

    Returns:
        str: A weather report for the city.
    """
    responses = [
        f"The weather in {city} is sunny with clear skies ☀️",
        f"It’s raining in {city}. Don’t forget your umbrella ☔",
        f"{city} is cloudy with a chance of showers ⛅"
    ]
    return random.choice(responses)
