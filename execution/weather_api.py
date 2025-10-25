"""
Weather API client using free OpenWeatherMap API.

Default location: Muzaffarnagar, Uttar Pradesh, India
"""

import aiohttp
import os
from typing import Dict, Any, Optional
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)


class WeatherAPI:
    """
    Free weather API client using OpenWeatherMap.
    
    Sign up for free API key at: https://openweathermap.org/api
    Free tier: 1,000 calls/day, 60 calls/minute
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather API client.
        
        Args:
            api_key: OpenWeatherMap API key (or set OPENWEATHER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Default location: Muzaffarnagar, UP, India
        self.default_location = {
            'city': 'Muzaffarnagar',
            'state': 'Uttar Pradesh',
            'country': 'IN',
            'lat': 29.4727,
            'lon': 77.7085
        }
        
        if not self.api_key:
            logger.warning(
                "No OpenWeatherMap API key found. "
                "Set OPENWEATHER_API_KEY environment variable or pass api_key parameter. "
                "Get free key at: https://openweathermap.org/api"
            )
    
    async def get_current_weather(
        self, 
        city: Optional[str] = None,
        country: str = 'IN',
        units: str = 'metric'
    ) -> Dict[str, Any]:
        """
        Get current weather for a location.
        
        Args:
            city: City name (default: Muzaffarnagar)
            country: Country code (default: IN for India)
            units: metric (Celsius) or imperial (Fahrenheit)
            
        Returns:
            Weather data dictionary
        """
        if not self.api_key:
            return self._get_demo_weather()
        
        city = city or self.default_location['city']
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city},{country}",
                'appid': self.api_key,
                'units': units
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_current_weather(data)
                    else:
                        error_msg = await response.text()
                        logger.error(f"Weather API error: {response.status} - {error_msg}")
                        return self._get_error_response(f"API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return self._get_error_response(str(e))
    
    async def get_forecast(
        self,
        city: Optional[str] = None,
        country: str = 'IN',
        units: str = 'metric',
        days: int = 5
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            city: City name (default: Muzaffarnagar)
            country: Country code (default: IN)
            units: metric or imperial
            days: Number of days (max 5 for free tier)
            
        Returns:
            Forecast data dictionary
        """
        if not self.api_key:
            return self._get_demo_forecast()
        
        city = city or self.default_location['city']
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': f"{city},{country}",
                'appid': self.api_key,
                'units': units,
                'cnt': min(days * 8, 40)  # 8 forecasts per day, max 40
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_forecast(data, days)
                    else:
                        error_msg = await response.text()
                        logger.error(f"Forecast API error: {response.status} - {error_msg}")
                        return self._get_error_response(f"API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return self._get_error_response(str(e))
    
    def _format_current_weather(self, data: Dict) -> Dict[str, Any]:
        """Format OpenWeatherMap response to our format."""
        return {
            'success': True,
            'location': {
                'city': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            },
            'current': {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility', 0),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).isoformat(),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).isoformat(),
            },
            'timestamp': datetime.fromtimestamp(data['dt']).isoformat(),
            'units': 'metric'
        }
    
    def _format_forecast(self, data: Dict, days: int) -> Dict[str, Any]:
        """Format forecast response."""
        forecasts = []
        
        for item in data['list'][:days * 8]:
            forecasts.append({
                'datetime': datetime.fromtimestamp(item['dt']).isoformat(),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max'],
                'pressure': item['main']['pressure'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
                'main': item['weather'][0]['main'],
                'wind_speed': item['wind']['speed'],
                'clouds': item['clouds']['all'],
                'pop': item.get('pop', 0) * 100  # Probability of precipitation
            })
        
        return {
            'success': True,
            'location': {
                'city': data['city']['name'],
                'country': data['city']['country'],
                'coordinates': {
                    'lat': data['city']['coord']['lat'],
                    'lon': data['city']['coord']['lon']
                }
            },
            'forecast': forecasts,
            'units': 'metric'
        }
    
    def _get_demo_weather(self) -> Dict[str, Any]:
        """Return demo weather data when API key is not available."""
        return {
            'success': True,
            'demo': True,
            'message': 'Using demo data. Set OPENWEATHER_API_KEY for real data.',
            'location': self.default_location,
            'current': {
                'temperature': 28.5,
                'feels_like': 30.2,
                'temp_min': 26.0,
                'temp_max': 32.0,
                'pressure': 1013,
                'humidity': 65,
                'description': 'partly cloudy',
                'main': 'Clouds',
                'wind_speed': 3.5,
                'clouds': 40,
                'visibility': 10000,
            },
            'timestamp': datetime.now().isoformat(),
            'units': 'metric'
        }
    
    def _get_demo_forecast(self) -> Dict[str, Any]:
        """Return demo forecast data."""
        return {
            'success': True,
            'demo': True,
            'message': 'Using demo data. Set OPENWEATHER_API_KEY for real data.',
            'location': self.default_location,
            'forecast': [
                {
                    'datetime': datetime.now().isoformat(),
                    'temperature': 28.5,
                    'description': 'partly cloudy',
                    'humidity': 65,
                    'wind_speed': 3.5
                }
            ],
            'units': 'metric'
        }
    
    def _get_error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            'success': False,
            'error': error,
            'location': self.default_location
        }
    
    def format_weather_text(self, weather_data: Dict) -> str:
        """
        Format weather data into human-readable text.
        
        Args:
            weather_data: Weather data from get_current_weather()
            
        Returns:
            Formatted text description
        """
        if not weather_data.get('success'):
            return f"Sorry, I couldn't fetch the weather: {weather_data.get('error', 'Unknown error')}"
        
        if weather_data.get('demo'):
            prefix = "[Demo Data] "
        else:
            prefix = ""
        
        loc = weather_data['location']
        curr = weather_data['current']
        
        city_name = loc.get('city', 'Muzaffarnagar')
        
        text = f"{prefix}Weather in {city_name}: "
        text += f"{curr['temperature']:.1f}°C, {curr['description']}. "
        text += f"Feels like {curr['feels_like']:.1f}°C. "
        text += f"Humidity: {curr['humidity']}%. "
        text += f"Wind: {curr['wind_speed']:.1f} m/s."
        
        return text


# Convenience function
async def get_weather(city: Optional[str] = None) -> str:
    """
    Quick function to get weather as text.
    
    Args:
        city: City name (default: Muzaffarnagar)
        
    Returns:
        Weather description text
    """
    api = WeatherAPI()
    data = await api.get_current_weather(city)
    return api.format_weather_text(data)
