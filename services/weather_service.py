"""
Weather Service for fetching weather information
"""
from typing import Dict, Any, Optional
from config import settings
import logging
import httpx

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap or similar"""

    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.WEATHER_API_KEY)

    async def fetch_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch weather data for a given location

        Args:
            location: City name or coordinates

        Returns:
            Dictionary with weather information
        """
        location = location or settings.DEFAULT_LOCATION

        if not self.is_configured():
            logger.warning("Weather API not configured")
            return {}

        try:
            async with httpx.AsyncClient() as client:
                # Fetch current weather
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": "imperial"  # Use 'metric' for Celsius
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    return {
                        "location": data.get("name"),
                        "temperature": data.get("main", {}).get("temp"),
                        "feels_like": data.get("main", {}).get("feels_like"),
                        "condition": data.get("weather", [{}])[0].get("main"),
                        "description": data.get("weather", [{}])[0].get("description"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "wind_speed": data.get("wind", {}).get("speed"),
                        "precipitation": data.get("rain", {}).get("1h", 0)
                    }
                else:
                    logger.error(f"Weather API error: {response.status_code}")
                    return {}

        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return {}
