"""External API client."""

import aiohttp
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta

from core.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """Client for external API integrations."""
    
    def __init__(self):
        """Initialize API client."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, datetime] = {}
    
    async def call_api(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        cache_ttl: int = 3600
    ) -> Dict[str, Any]:
        """
        Call external API.
        
        Args:
            url: API endpoint
            method: HTTP method
            headers: Request headers
            data: Request data
            cache_ttl: Cache TTL in seconds
            
        Returns:
            API response
        """
        # Check cache
        cache_key = f"{method}:{url}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.utcnow() < cached['expires']:
                logger.info(f"Cache hit: {url}")
                return cached['data']
        
        # Make request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    # Cache result
                    self.cache[cache_key] = {
                        'data': result,
                        'expires': datetime.utcnow() + timedelta(seconds=cache_ttl)
                    }
                    
                    logger.info(f"API call successful: {url}")
                    return result
                    
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {"error": str(e)}
    
    async def get_weather(self, location: str, api_key: str) -> Dict[str, Any]:
        """Get weather data."""
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        return await self.call_api(url)
    
    async def search_web(self, query: str) -> Dict[str, Any]:
        """Search web (DuckDuckGo)."""
        # Placeholder - would use actual search API
        return {"results": [], "query": query}
