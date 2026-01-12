import httpx
import os
from typing import Dict, Any, Optional

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
BASE_URL = "http://api.weatherapi.com/v1"

async def get_weather(location: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches weather data from WeatherAPI.com.
    If date is provided, uses the forecast endpoint (or future/history depending on specific needs, 
    but Forecast handles up to 14 days).
    If date is None, defaults to current weather.
    """
    if not WEATHERAPI_KEY:
        raise ValueError("WEATHERAPI_KEY environment variable is not set")

    async with httpx.AsyncClient() as client:
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
        }
        
        # If a specific date is requested, we use the forecast endpoint.
        # Note: WeatherAPI 'forecast' endpoint handles 'dt' parameter for specific dates.
        # If no date is provided, we still often want forecast for 'today' to get max/min temps,
        # but strictly speaking 'current' is lighter. 
        # However, users often ask "what's the weather" implying a general outlook (high/low).
        # We will use forecast for 1 day by default if no date specified to be safe, 
        # or just current. Let's stick to Forecast to get more context (condition text, etc).
        
        endpoint = "forecast.json"
        
        if date:
            params["dt"] = date
        else:
            params["days"] = "1"
            
        response = await client.get(f"{BASE_URL}/{endpoint}", params=params)

        if response.status_code != 200:
            # We return a simplified error structure or raise
            return {"error": f"WeatherAPI returned {response.status_code}: {response.text}"}
            
        return response.json()
