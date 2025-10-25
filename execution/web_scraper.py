"""Web scraping functionality."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import asyncio

from core.models import Document
from core.logger import get_logger

logger = get_logger(__name__)


class WebScraper:
    """Web scraping and content extraction."""
    
    def __init__(self, user_agent: Optional[str] = None):
        """Initialize web scraper."""
        self.user_agent = user_agent or "OnDeviceAssistant/0.1.0"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    async def scrape_url(self, url: str) -> Document:
        """
        Scrape content from URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Document with scraped content
        """
        return await asyncio.to_thread(self._scrape_url_sync, url)
    
    def _scrape_url_sync(self, url: str) -> Document:
        """Synchronous scraping."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)
            
            # Extract metadata
            title = soup.title.string if soup.title else url
            
            doc = Document(
                id=f"web_{hash(url)}",
                text=text[:5000],  # Limit size
                source="web",
                metadata={
                    "url": url,
                    "title": title,
                    "status_code": response.status_code
                }
            )
            
            logger.info(f"Scraped {url}: {len(text)} chars")
            return doc
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return Document(
                id=f"web_{hash(url)}",
                text="",
                source="web",
                metadata={"url": url, "error": str(e)}
            )
