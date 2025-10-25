"""Real-time data integration for weather, news, search, and knowledge."""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp

from core.logger import get_logger

logger = get_logger(__name__)


class WeatherService:
    """Weather data service."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather service.
        
        Args:
            api_key: OpenWeatherMap API key (optional)
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for location.
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data
        """
        if not self.api_key:
            return {"error": "Weather API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "location": data["name"],
                            "temperature": data["main"]["temp"],
                            "feels_like": data["main"]["feels_like"],
                            "humidity": data["main"]["humidity"],
                            "description": data["weather"][0]["description"],
                            "wind_speed": data["wind"]["speed"]
                        }
                    else:
                        return {"error": f"Weather API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return {"error": str(e)}
    
    async def get_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get weather forecast.
        
        Args:
            location: City name
            days: Number of days
            
        Returns:
            Forecast data
        """
        if not self.api_key:
            return [{"error": "Weather API key not configured"}]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/forecast"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8  # 8 forecasts per day
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecasts = []
                        
                        for item in data["list"]:
                            forecasts.append({
                                "datetime": item["dt_txt"],
                                "temperature": item["main"]["temp"],
                                "description": item["weather"][0]["description"]
                            })
                        
                        return forecasts
                    else:
                        return [{"error": f"Forecast API error: {response.status}"}]
                        
        except Exception as e:
            logger.error(f"Forecast fetch failed: {e}")
            return [{"error": str(e)}]


class NewsService:
    """News aggregation service."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize news service.
        
        Args:
            api_key: NewsAPI key (optional)
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    async def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top news headlines.
        
        Args:
            country: Country code
            category: News category
            limit: Number of articles
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            return [{"error": "News API key not configured"}]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/top-headlines"
                params = {
                    "country": country,
                    "apiKey": self.api_key,
                    "pageSize": limit
                }
                
                if category:
                    params["category"] = category
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for article in data.get("articles", []):
                            articles.append({
                                "title": article["title"],
                                "description": article.get("description", ""),
                                "source": article["source"]["name"],
                                "url": article["url"],
                                "published_at": article["publishedAt"]
                            })
                        
                        return articles
                    else:
                        return [{"error": f"News API error: {response.status}"}]
                        
        except Exception as e:
            logger.error(f"News fetch failed: {e}")
            return [{"error": str(e)}]
    
    async def search_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search news articles.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            return [{"error": "News API key not configured"}]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/everything"
                params = {
                    "q": query,
                    "apiKey": self.api_key,
                    "pageSize": limit,
                    "sortBy": "relevancy"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for article in data.get("articles", []):
                            articles.append({
                                "title": article["title"],
                                "description": article.get("description", ""),
                                "source": article["source"]["name"],
                                "url": article["url"],
                                "published_at": article["publishedAt"]
                            })
                        
                        return articles
                    else:
                        return [{"error": f"News search error: {response.status}"}]
                        
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return [{"error": str(e)}]


class SearchService:
    """Web search service."""
    
    def __init__(self):
        """Initialize search service."""
        self.search_available = False
        
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.search_available = True
            logger.info("DuckDuckGo search initialized")
        except ImportError:
            logger.warning("DuckDuckGo search not available")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            Search results
        """
        if not self.search_available:
            return [{"error": "Search service not available"}]
        
        try:
            results = await asyncio.to_thread(
                self._search_sync,
                query,
                limit
            )
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [{"error": str(e)}]
    
    def _search_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Synchronous search."""
        results = []
        
        for result in self.ddgs.text(query, max_results=limit):
            results.append({
                "title": result.get("title", ""),
                "snippet": result.get("body", ""),
                "url": result.get("href", "")
            })
        
        return results


class KnowledgeGraphService:
    """Knowledge graph and Wikipedia service."""
    
    def __init__(self):
        """Initialize knowledge graph service."""
        self.wikipedia_available = False
        
        try:
            import wikipedia
            self.wikipedia = wikipedia
            self.wikipedia_available = True
            logger.info("Wikipedia service initialized")
        except ImportError:
            logger.warning("Wikipedia not available")
    
    async def get_summary(self, topic: str, sentences: int = 3) -> Dict[str, Any]:
        """
        Get Wikipedia summary.
        
        Args:
            topic: Topic to search
            sentences: Number of sentences
            
        Returns:
            Summary data
        """
        if not self.wikipedia_available:
            return {"error": "Wikipedia not available"}
        
        try:
            summary = await asyncio.to_thread(
                self.wikipedia.summary,
                topic,
                sentences=sentences
            )
            
            page = await asyncio.to_thread(
                self.wikipedia.page,
                topic
            )
            
            return {
                "title": page.title,
                "summary": summary,
                "url": page.url,
                "categories": page.categories[:5]
            }
            
        except self.wikipedia.exceptions.DisambiguationError as e:
            return {
                "error": "Multiple results found",
                "options": e.options[:5]
            }
        except self.wikipedia.exceptions.PageError:
            return {"error": f"No Wikipedia page found for '{topic}'"}
        except Exception as e:
            logger.error(f"Wikipedia fetch failed: {e}")
            return {"error": str(e)}
    
    async def search(self, query: str, limit: int = 5) -> List[str]:
        """
        Search Wikipedia.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of page titles
        """
        if not self.wikipedia_available:
            return []
        
        try:
            results = await asyncio.to_thread(
                self.wikipedia.search,
                query,
                results=limit
            )
            return results
            
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []


class RealTimeDataManager:
    """Manager for all real-time data services."""
    
    def __init__(
        self,
        weather_api_key: Optional[str] = None,
        news_api_key: Optional[str] = None
    ):
        """
        Initialize real-time data manager.
        
        Args:
            weather_api_key: Weather API key
            news_api_key: News API key
        """
        self.weather = WeatherService(weather_api_key)
        self.news = NewsService(news_api_key)
        self.search = SearchService()
        self.knowledge = KnowledgeGraphService()
        
        logger.info("Real-time data manager initialized")
    
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather data."""
        return await self.weather.get_weather(location)
    
    async def get_news(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get news articles."""
        if query:
            return await self.news.search_news(query, limit)
        else:
            return await self.news.get_top_headlines(category=category, limit=limit)
    
    async def search_web(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the web."""
        return await self.search.search(query, limit)
    
    async def get_knowledge(self, topic: str) -> Dict[str, Any]:
        """Get knowledge from Wikipedia."""
        return await self.knowledge.get_summary(topic)
    
    async def search_knowledge(self, query: str) -> List[str]:
        """Search knowledge base."""
        return await self.knowledge.search(query)
