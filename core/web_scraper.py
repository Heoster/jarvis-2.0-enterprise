"""
Advanced Web Scraping Engine for Jarvis
Real-time data gathering, web scraping, and content extraction
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
from core.logger import get_logger
from core.codeex_personality import CodeexPersonality

logger = get_logger(__name__)


class AdvancedWebScraper:
    """Advanced web scraping with DuckDuckGo search and content extraction"""
    
    def __init__(self):
        self.personality = CodeexPersonality()
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Cache for scraped content
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
        
        logger.info("Advanced Web Scraper initialized for Jarvis")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo and return results
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of search results with title, url, snippet
        """
        try:
            logger.info(f"Searching DuckDuckGo for: {query}")
            
            # Check cache
            cache_key = f"ddg_{query}_{max_results}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if (datetime.now().timestamp() - cached_time) < self.cache_duration:
                    logger.info("Returning cached DuckDuckGo results")
                    return cached_data
            
            session = await self._get_session()
            
            # DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            async with session.get(search_url) as response:
                if response.status != 200:
                    logger.error(f"DuckDuckGo search failed: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                result_divs = soup.find_all('div', class_='result')
                
                for div in result_divs[:max_results]:
                    try:
                        # Extract title and URL
                        title_tag = div.find('a', class_='result__a')
                        if not title_tag:
                            continue
                        
                        title = title_tag.get_text(strip=True)
                        url = title_tag.get('href', '')
                        
                        # Extract snippet
                        snippet_tag = div.find('a', class_='result__snippet')
                        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
                        
                        if title and url:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'DuckDuckGo'
                            })
                    
                    except Exception as e:
                        logger.warning(f"Error parsing search result: {e}")
                        continue
                
                # Cache results
                self.cache[cache_key] = (datetime.now().timestamp(), results)
                
                logger.info(f"Found {len(results)} DuckDuckGo results")
                return results
        
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    async def scrape_webpage(self, url: str, extract_text: bool = True) -> Dict[str, Any]:
        """
        Scrape content from a webpage
        
        Args:
            url: URL to scrape
            extract_text: Whether to extract main text content
        
        Returns:
            Dictionary with scraped content
        """
        try:
            logger.info(f"Scraping webpage: {url}")
            
            # Check cache
            cache_key = f"page_{url}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if (datetime.now().timestamp() - cached_time) < self.cache_duration:
                    logger.info("Returning cached webpage content")
                    return cached_data
            
            session = await self._get_session()
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return {
                        'error': f'HTTP {response.status}',
                        'url': url
                    }
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract metadata
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else ''
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ''
                
                # Extract main content with better formatting
                content = ''
                if extract_text:
                    # Remove script and style elements
                    for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        script.decompose()
                    
                    # Try to find main content areas in order of preference
                    main_content = (
                        soup.find('main') or 
                        soup.find('article') or 
                        soup.find('div', class_=re.compile(r'content|main|article|post', re.I)) or
                        soup.find('body')
                    )
                    
                    if main_content:
                        # Extract paragraphs for better content
                        paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
                        
                        if paragraphs:
                            # Build content from paragraphs with better formatting
                            content_parts = []
                            for para in paragraphs[:50]:  # Limit to first 50 elements
                                text = para.get_text(strip=True)
                                if text and len(text) > 15:  # Only include substantial text
                                    # Add heading markers with clear formatting
                                    if para.name == 'h1':
                                        content_parts.append(f"\n\n═══ {text.upper()} ═══\n")
                                    elif para.name == 'h2':
                                        content_parts.append(f"\n\n▸ {text}\n")
                                    elif para.name in ['h3', 'h4']:
                                        content_parts.append(f"\n• {text}\n")
                                    elif para.name == 'li':
                                        content_parts.append(f"  - {text}")
                                    else:
                                        content_parts.append(text)
                            
                            content = '\n'.join(content_parts)
                        else:
                            # Fallback to all text
                            content = main_content.get_text(separator=' ', strip=True)
                        
                        # Clean up excessive whitespace while preserving formatting
                        # Replace multiple spaces with single space
                        content = re.sub(r' +', ' ', content)
                        # Replace more than 3 newlines with 2 newlines
                        content = re.sub(r'\n{4,}', '\n\n', content)
                        content = content.strip()
                        
                        # Limit to 10000 chars for better content (increased from 8000)
                        if len(content) > 10000:
                            content = content[:10000]
                
                # Extract links
                links = []
                for link in soup.find_all('a', href=True)[:20]:
                    href = link.get('href')
                    link_text = link.get_text(strip=True)
                    if href and link_text:
                        full_url = urljoin(url, href)
                        links.append({
                            'text': link_text,
                            'url': full_url
                        })
                
                result = {
                    'url': url,
                    'title': title_text,
                    'description': description,
                    'content': content,
                    'links': links,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Cache result
                self.cache[cache_key] = (datetime.now().timestamp(), result)
                
                logger.info(f"Successfully scraped: {title_text}")
                return result
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout scraping: {url}")
            return {'error': 'Timeout', 'url': url}
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {'error': str(e), 'url': url}
    
    async def search_and_scrape(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Search DuckDuckGo and scrape top results
        
        Args:
            query: Search query
            num_results: Number of results to scrape
        
        Returns:
            Dictionary with search results and scraped content
        """
        try:
            logger.info(f"Search and scrape for: {query}")
            
            # Search DuckDuckGo
            search_results = await self.search_duckduckgo(query, max_results=num_results)
            
            if not search_results:
                return {
                    'query': query,
                    'results': [],
                    'error': 'No search results found'
                }
            
            # Scrape top results
            scraped_content = []
            for result in search_results[:num_results]:
                url = result['url']
                logger.info(f"Scraping: {url}")
                scraped = await self.scrape_webpage(url)
                
                if 'error' not in scraped:
                    content = scraped.get('content', '')
                    
                    # Ensure we have meaningful content
                    if content and len(content) > 100:
                        scraped_content.append({
                            'title': result['title'],
                            'url': url,
                            'snippet': result['snippet'],
                            'content': content[:2000],  # First 2000 chars for preview
                            'full_content': content,  # Full content
                            'description': scraped.get('description', ''),
                            'scraped_at': scraped.get('scraped_at', '')
                        })
                        logger.info(f"Successfully scraped {len(content)} chars from {url}")
                    else:
                        logger.warning(f"Insufficient content from {url}")
                else:
                    logger.warning(f"Error scraping {url}: {scraped.get('error')}")
            
            return {
                'query': query,
                'search_results': search_results,
                'scraped_content': scraped_content,
                'total_results': len(search_results),
                'scraped_count': len(scraped_content)
            }
        
        except Exception as e:
            logger.error(f"Search and scrape error: {e}")
            return {
                'query': query,
                'error': str(e)
            }
    
    async def extract_structured_data(self, url: str) -> Dict[str, Any]:
        """
        Extract structured data from webpage (JSON-LD, microdata, etc.)
        
        Args:
            url: URL to extract from
        
        Returns:
            Structured data dictionary
        """
        try:
            session = await self._get_session()
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return {'error': f'HTTP {response.status}'}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                structured_data = {}
                
                # Extract JSON-LD
                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                if json_ld_scripts:
                    import json
                    structured_data['json_ld'] = []
                    for script in json_ld_scripts:
                        try:
                            data = json.loads(script.string)
                            structured_data['json_ld'].append(data)
                        except:
                            pass
                
                # Extract Open Graph tags
                og_tags = {}
                for tag in soup.find_all('meta', property=re.compile(r'^og:')):
                    property_name = tag.get('property', '').replace('og:', '')
                    og_tags[property_name] = tag.get('content', '')
                
                if og_tags:
                    structured_data['open_graph'] = og_tags
                
                # Extract Twitter Card tags
                twitter_tags = {}
                for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
                    name = tag.get('name', '').replace('twitter:', '')
                    twitter_tags[name] = tag.get('content', '')
                
                if twitter_tags:
                    structured_data['twitter_card'] = twitter_tags
                
                return structured_data
        
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {'error': str(e)}
    
    def format_search_results(self, results: Dict[str, Any]) -> str:
        """
        Format search results with Codeex personality
        
        Args:
            results: Search results dictionary
        
        Returns:
            Formatted string with magical touch
        """
        if 'error' in results:
            return self.personality.wrap_response(
                f"I encountered an issue searching: {results['error']}",
                'error'
            )
        
        query = results.get('query', '')
        scraped = results.get('scraped_content', [])
        
        if not scraped:
            return self.personality.wrap_response(
                f"I searched for '{query}' but couldn't find detailed information.",
                'learning'
            )
        
        # Build magical response
        response = f"🔍 **Search Results for '{query}'** ✨\n\n"
        
        for i, item in enumerate(scraped[:3], 1):
            response += f"**{i}. {item['title']}**\n"
            response += f"🔗 {item['url']}\n"
            response += f"📝 {item['snippet'][:200]}...\n\n"
            
            if item.get('content'):
                # Extract key information
                content_preview = item['content'][:300]
                response += f"💡 Key Info: {content_preview}...\n\n"
        
        response += self.personality.get_encouragement()
        
        return response
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("Web scraper cache cleared")


# Singleton instance
_scraper_instance = None

async def get_web_scraper() -> AdvancedWebScraper:
    """Get or create web scraper instance"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = AdvancedWebScraper()
    return _scraper_instance
