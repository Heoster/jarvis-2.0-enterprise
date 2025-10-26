"""
Web search and scraping tool.
Standardized interface for web search operations.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool, ToolResult
from core.web_scraper import get_web_scraper
from core.constants import ResponseLimits


class WebSearchTool(BaseTool):
    """Web search and scraping tool with standardized interface"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.web_scraper = None
    
    async def _ensure_scraper(self):
        """Ensure web scraper is initialized"""
        if self.web_scraper is None:
            self.web_scraper = await get_web_scraper()
    
    def get_required_fields(self) -> List[str]:
        """Get required input fields"""
        return ['query']
    
    def get_optional_fields(self) -> List[str]:
        """Get optional input fields"""
        return ['num_results', 'scrape_content', 'timeout']
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        if 'query' not in input_data:
            return False
        
        query = input_data['query']
        if not isinstance(query, str) or len(query.strip()) == 0:
            return False
        
        # Validate optional parameters
        if 'num_results' in input_data:
            num_results = input_data['num_results']
            if not isinstance(num_results, int) or num_results < 1 or num_results > 10:
                return False
        
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute web search and scraping.
        
        Args:
            input_data: Search parameters
                - query (str): Search query
                - num_results (int, optional): Number of results (default: 3)
                - scrape_content (bool, optional): Whether to scrape content (default: True)
                - timeout (float, optional): Request timeout
        
        Returns:
            ToolResult with search results
        """
        try:
            await self._ensure_scraper()
            
            query = input_data['query'].strip()
            num_results = input_data.get('num_results', ResponseLimits.MAX_SEARCH_RESULTS)
            scrape_content = input_data.get('scrape_content', True)
            
            self.logger.info(f"Searching for: {query} (results: {num_results})")
            
            if scrape_content:
                # Full search and scrape
                results = await self.web_scraper.search_and_scrape(query, num_results)
            else:
                # Search only
                results = await self.web_scraper.search_duckduckgo(query, num_results)
                results = {'query': query, 'search_results': results}
            
            if results and not results.get('error'):
                metadata = {
                    'query': query,
                    'num_results_requested': num_results,
                    'num_results_found': len(results.get('scraped_content', results.get('search_results', []))),
                    'scrape_enabled': scrape_content
                }
                
                return self._create_success_result(results, metadata)
            else:
                error_msg = results.get('error', 'No results found') if results else 'Search failed'
                return self._create_error_result(error_msg)
                
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return self._create_error_result(str(e))
    
    async def search_only(self, query: str, num_results: int = 5) -> ToolResult:
        """
        Perform search without scraping content.
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            ToolResult with search results
        """
        return await self.execute({
            'query': query,
            'num_results': num_results,
            'scrape_content': False
        })
    
    async def search_and_scrape(self, query: str, num_results: int = 3) -> ToolResult:
        """
        Perform search and scrape content.
        
        Args:
            query: Search query
            num_results: Number of results to scrape
            
        Returns:
            ToolResult with scraped content
        """
        return await self.execute({
            'query': query,
            'num_results': num_results,
            'scrape_content': True
        })
    
    async def health_check(self) -> bool:
        """Check if web search is working"""
        try:
            await self._ensure_scraper()
            # Try a simple search
            test_result = await self.web_scraper.search_duckduckgo("test", 1)
            return isinstance(test_result, list)
        except Exception as e:
            self.logger.error(f"Web search health check failed: {e}")
            return False