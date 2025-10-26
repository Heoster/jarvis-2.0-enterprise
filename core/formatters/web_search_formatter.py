"""
Web search results formatter.
Formats web search and scraping results with clean, readable output.
"""

from typing import Dict, Any, List
from .base_formatter import ResponseFormatter
from core.constants import ResponseLimits


class WebSearchFormatter(ResponseFormatter):
    """Format web search results with detailed content"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format web search results.
        
        Args:
            data: Web search results data
            
        Returns:
            Formatted search results string
        """
        query = data.get('query', '')
        scraped_content = data.get('scraped_content', [])
        search_results = data.get('search_results', [])
        
        if not scraped_content and not search_results:
            return self.format_no_data(f"No results found for '{query}'")
        
        # Build response
        response = self.add_header(f"Search Results for '{query}'", self.emojis['search'])
        
        # Show scraped content if available
        if scraped_content:
            response += self._format_scraped_content(scraped_content)
        elif search_results:
            response += self._format_search_results(search_results)
        
        # Add summary
        total_results = len(scraped_content) or len(search_results)
        response += self.add_footer(f"Found {total_results} results")
        
        # Add suggestions
        response += self._add_search_suggestions()
        
        return response
    
    def _format_scraped_content(self, scraped_content: List[Dict[str, Any]]) -> str:
        """Format scraped content with full details"""
        response = f"✅ Successfully scraped {len(scraped_content)} pages with detailed content:\n\n"
        
        for i, item in enumerate(scraped_content, 1):
            response += self.add_subsection("Result", i)
            
            # Title
            title = item.get('title', 'No title')
            response += f"**TITLE:** {title}\n\n"
            
            # Source
            domain = self.extract_domain(item.get('url', ''))
            response += f"🌐 **SOURCE:** {domain}\n\n"
            
            # Search snippet
            if item.get('snippet'):
                response += f"📝 **SEARCH SUMMARY:**\n{item['snippet']}\n\n"
            
            # Meta description
            if item.get('description') and item['description'] != item.get('snippet'):
                response += f"📋 **PAGE DESCRIPTION:**\n{item['description']}\n\n"
            
            # Main content
            if item.get('content'):
                content = item['content'].strip()
                display_content = self.truncate_text(content, ResponseLimits.MAX_CONTENT_LENGTH)
                
                response += f"📖 **SCRAPED CONTENT:**\n"
                response += f"{self.section_sep}\n"
                response += f"{display_content}\n"
                response += f"{self.section_sep}\n"
                response += f"(Showing {len(display_content)} of {len(content)} characters)\n\n"
                
                # Show full content availability
                if item.get('full_content'):
                    full_len = len(item['full_content'])
                    response += f"💾 Full content available: {full_len} characters total\n"
        
        return response
    
    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Format basic search results without scraped content"""
        response = f"📋 Found {len(search_results)} search results:\n\n"
        
        for i, item in enumerate(search_results[:ResponseLimits.MAX_SEARCH_RESULTS], 1):
            title = item.get('title', 'No title')
            domain = self.extract_domain(item.get('url', ''))
            snippet = item.get('snippet', '')
            
            response += f"{i}. **{title}**\n"
            response += f"   🌐 {domain}\n"
            
            if snippet:
                truncated_snippet = self.truncate_text(snippet, 200)
                response += f"   📝 {truncated_snippet}\n"
            
            response += "\n"
        
        return response
    
    def _add_search_suggestions(self) -> str:
        """Add helpful suggestions for search results"""
        suggestions = [
            "Search for more specific information?",
            "Explore any of these sources in more detail?",
            "Summarize the key points from these results?"
        ]
        
        response = "\nWould you like me to:\n"
        response += self.format_list_items(suggestions)
        response += "\n"
        
        return response
    
    def format_search_error(self, query: str, error: str) -> str:
        """
        Format search error message.
        
        Args:
            query: Original search query
            error: Error message
            
        Returns:
            Formatted error message
        """
        response = self.add_header("Search Error", self.emojis['error'])
        response += f"❌ Failed to search for '{query}'\n\n"
        response += f"Error: {error}\n"
        response += self.add_footer("Please try a different query")
        
        return response
    
    def format_search_timeout(self, query: str) -> str:
        """
        Format search timeout message.
        
        Args:
            query: Original search query
            
        Returns:
            Formatted timeout message
        """
        response = self.add_header("Search Timeout", self.emojis['warning'])
        response += f"⏰ Search for '{query}' timed out\n\n"
        response += "This might be due to:\n"
        response += self.format_list_items([
            "Network connectivity issues",
            "High server load",
            "Complex search query"
        ])
        response += "\n"
        response += self.add_footer("Please try again with a simpler query")
        
        return response