"""
News API client using free NewsAPI.org.

Default country: India (IN)
"""

import aiohttp
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from core.logger import get_logger

logger = get_logger(__name__)


class NewsAPI:
    """
    Free news API client using NewsAPI.org.
    
    Sign up for free API key at: https://newsapi.org/
    Free tier: 100 requests/day, articles from last 30 days
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize news API client.
        
        Args:
            api_key: NewsAPI.org API key (or set NEWS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('NEWS_API_KEY', '')
        self.base_url = "https://newsapi.org/v2"
        
        # Default settings for India
        self.default_country = 'in'  # India
        self.default_language = 'en'  # English
        
        if not self.api_key:
            logger.warning(
                "No NewsAPI key found. "
                "Set NEWS_API_KEY environment variable or pass api_key parameter. "
                "Get free key at: https://newsapi.org/"
            )
    
    async def get_top_headlines(
        self,
        country: Optional[str] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get top headlines from India.
        
        Args:
            country: Country code (default: 'in' for India)
            category: business, entertainment, general, health, science, sports, technology
            query: Keywords to search for
            page_size: Number of articles (max 100)
            
        Returns:
            News articles dictionary
        """
        if not self.api_key:
            return self._get_demo_news()
        
        country = country or self.default_country
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'pageSize': min(page_size, 100)
            }
            
            if category:
                params['category'] = category
            
            if query:
                params['q'] = query
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news_response(data)
                    else:
                        error_msg = await response.text()
                        logger.error(f"News API error: {response.status} - {error_msg}")
                        return self._get_error_response(f"API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return self._get_error_response(str(e))
    
    async def search_news(
        self,
        query: str,
        language: Optional[str] = None,
        sort_by: str = 'publishedAt',
        page_size: int = 10,
        from_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Search for news articles.
        
        Args:
            query: Keywords to search for
            language: Language code (default: 'en')
            sort_by: relevancy, popularity, or publishedAt
            page_size: Number of articles (max 100)
            from_date: Start date for articles
            
        Returns:
            News articles dictionary
        """
        if not self.api_key:
            return self._get_demo_news(query=query)
        
        language = language or self.default_language
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'apiKey': self.api_key,
                'q': query,
                'language': language,
                'sortBy': sort_by,
                'pageSize': min(page_size, 100)
            }
            
            if from_date:
                params['from'] = from_date.isoformat()
            else:
                # Default: last 7 days
                params['from'] = (datetime.now() - timedelta(days=7)).isoformat()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news_response(data)
                    else:
                        error_msg = await response.text()
                        logger.error(f"News search error: {response.status} - {error_msg}")
                        return self._get_error_response(f"API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return self._get_error_response(str(e))
    
    async def get_news_by_category(
        self,
        category: str,
        country: Optional[str] = None,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get news by category for India.
        
        Args:
            category: business, entertainment, general, health, science, sports, technology
            country: Country code (default: 'in')
            page_size: Number of articles
            
        Returns:
            News articles dictionary
        """
        return await self.get_top_headlines(
            country=country,
            category=category,
            page_size=page_size
        )
    
    def _format_news_response(self, data: Dict) -> Dict[str, Any]:
        """Format NewsAPI response to our format."""
        articles = []
        
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'image_url': article.get('urlToImage', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'author': article.get('author', 'Unknown'),
                'published_at': article.get('publishedAt', ''),
            })
        
        return {
            'success': True,
            'total_results': data.get('totalResults', 0),
            'articles': articles,
            'country': self.default_country
        }
    
    def _get_demo_news(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Return demo news data when API key is not available."""
        demo_articles = [
            {
                'title': 'India Tech News: AI Development Accelerates',
                'description': 'Indian tech sector sees rapid growth in AI and machine learning applications.',
                'content': 'Demo article content...',
                'url': 'https://example.com/news1',
                'image_url': '',
                'source': 'Demo News',
                'author': 'Demo Author',
                'published_at': datetime.now().isoformat(),
            },
            {
                'title': 'Weather Update: Monsoon Season Approaches',
                'description': 'Meteorological department predicts normal monsoon this year.',
                'content': 'Demo article content...',
                'url': 'https://example.com/news2',
                'image_url': '',
                'source': 'Demo Weather News',
                'author': 'Demo Author',
                'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            },
            {
                'title': 'Sports: Cricket Team Wins Series',
                'description': 'Indian cricket team secures victory in international series.',
                'content': 'Demo article content...',
                'url': 'https://example.com/news3',
                'image_url': '',
                'source': 'Demo Sports',
                'author': 'Demo Author',
                'published_at': (datetime.now() - timedelta(hours=5)).isoformat(),
            }
        ]
        
        if query:
            # Filter demo articles by query
            demo_articles = [
                a for a in demo_articles 
                if query.lower() in a['title'].lower() or query.lower() in a['description'].lower()
            ]
        
        return {
            'success': True,
            'demo': True,
            'message': 'Using demo data. Set NEWS_API_KEY for real news.',
            'total_results': len(demo_articles),
            'articles': demo_articles,
            'country': 'in'
        }
    
    def _get_error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            'success': False,
            'error': error,
            'articles': [],
            'country': self.default_country
        }
    
    def format_news_text(
        self, 
        news_data: Dict, 
        max_articles: int = 5
    ) -> str:
        """
        Format news data into human-readable text.
        
        Args:
            news_data: News data from get_top_headlines() or search_news()
            max_articles: Maximum number of articles to include
            
        Returns:
            Formatted text description
        """
        if not news_data.get('success'):
            return f"Sorry, I couldn't fetch the news: {news_data.get('error', 'Unknown error')}"
        
        if news_data.get('demo'):
            prefix = "[Demo Data] "
        else:
            prefix = ""
        
        articles = news_data.get('articles', [])[:max_articles]
        
        if not articles:
            return f"{prefix}No news articles found."
        
        text = f"{prefix}Here are the top {len(articles)} news headlines from India:\n\n"
        
        for i, article in enumerate(articles, 1):
            text += f"{i}. {article['title']}\n"
            if article.get('description'):
                text += f"   {article['description']}\n"
            text += f"   Source: {article['source']}\n\n"
        
        return text.strip()
    
    def format_news_summary(self, news_data: Dict) -> str:
        """
        Format news data into a brief summary.
        
        Args:
            news_data: News data from get_top_headlines() or search_news()
            
        Returns:
            Brief summary text
        """
        if not news_data.get('success'):
            return f"Sorry, I couldn't fetch the news: {news_data.get('error', 'Unknown error')}"
        
        articles = news_data.get('articles', [])
        
        if not articles:
            return "No news articles found."
        
        if news_data.get('demo'):
            prefix = "[Demo] "
        else:
            prefix = ""
        
        # Just show titles
        titles = [a['title'] for a in articles[:5]]
        text = f"{prefix}Top news from India: " + "; ".join(titles)
        
        return text


# Convenience functions
async def get_india_news(category: Optional[str] = None, count: int = 5) -> str:
    """
    Quick function to get India news as text.
    
    Args:
        category: Optional category filter
        count: Number of articles
        
    Returns:
        News description text
    """
    api = NewsAPI()
    data = await api.get_top_headlines(category=category, page_size=count)
    return api.format_news_text(data, max_articles=count)


async def search_india_news(query: str, count: int = 5) -> str:
    """
    Quick function to search India news as text.
    
    Args:
        query: Search query
        count: Number of articles
        
    Returns:
        News description text
    """
    api = NewsAPI()
    data = await api.search_news(query, page_size=count)
    return api.format_news_text(data, max_articles=count)
