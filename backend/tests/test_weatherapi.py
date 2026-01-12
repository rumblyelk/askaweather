import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.weatherapi import get_weather

@pytest.mark.asyncio
async def test_get_weather_success():
    # Mock data that WeatherAPI would return
    mock_response_data = {
        "location": {"name": "Berlin", "country": "Germany"},
        "current": {
            "temp_c": 15.0,
            "condition": {"text": "Partly cloudy"},
            "wind_kph": 10.0,
            "humidity": 60
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2024-03-20",
                    "day": {
                        "maxtemp_c": 18.0,
                        "mintemp_c": 10.0,
                        "condition": {"text": "Sunny"},
                        "maxwind_kph": 12.0,
                        "avghumidity": 55,
                        "daily_chance_of_rain": 0
                    }
                }
            ]
        }
    }
    
    # We need to mock os.getenv to return a dummy key so the function doesn't bail early
    with patch("os.getenv", return_value="dummy_key"):
        # We also need to reload the module or patch the variable directly because
        # it's read at module level in app/weatherapi.py
        with patch("app.weatherapi.WEATHERAPI_KEY", "dummy_key"):
            # Mock the httpx.AsyncClient context manager
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                # Ensure the context manager return value (client instance) is an AsyncMock
                mock_client_cls.return_value.__aenter__.return_value = mock_client
                
                # IMPORTANT: mock_response must be a standard MagicMock, NOT AsyncMock
                # because response.json() is a synchronous method in httpx.
                # If it were AsyncMock, calling .json() would return a coroutine.
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_response_data
                
                # client.get is async, so it returns a coroutine that yields mock_response
                mock_client.get.return_value = mock_response

                # Test current weather call (no date)
                result = await get_weather("Berlin", None)
                
                assert result["location"]["name"] == "Berlin"
                assert result["current"]["temp_c"] == 15.0
                
                # Test forecast call (with date)
                result_forecast = await get_weather("Berlin", "2024-03-20")
                assert result_forecast["forecast"]["forecastday"][0]["date"] == "2024-03-20"

@pytest.mark.asyncio
async def test_get_weather_api_error():
    with patch("app.weatherapi.WEATHERAPI_KEY", "dummy_key"):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            
            mock_client.get.return_value = mock_response

            result = await get_weather("InvalidCity", None)
            assert "error" in result
            assert "WeatherAPI returned 400" in result["error"]
