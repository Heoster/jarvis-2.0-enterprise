"""
Formatter Factory implementing Factory pattern.
Creates appropriate formatters for different data types.
"""

from typing import Dict, Any, Optional
from .base_formatter import ResponseFormatter
from .web_search_formatter import WebSearchFormatter
from .financial_formatter import FinancialFormatter
from .railway_formatter import RailwayFormatter
from .entertainment_formatter import EntertainmentFormatter

from core.logger import get_logger

logger = get_logger(__name__)


class DefaultFormatter(ResponseFormatter):
    """Default formatter for unspecified data types"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format generic data"""
        if not data:
            return self.format_no_data("No data available")
        
        response = self.add_header("Information", "📋")
        
        # Try to format the data in a readable way
        if isinstance(data, dict):
            response += self.format_key_value_pairs(data)
        elif isinstance(data, list):
            response += self.format_list_items([str(item) for item in data])
        else:
            response += str(data)
        
        response += self.add_footer("Information retrieved")
        
        return response


class FormatterFactory:
    """
    Factory class for creating appropriate formatters.
    Implements Factory pattern for response formatting.
    """
    
    def __init__(self):
        """Initialize formatter factory"""
        self.formatters = {
            'web_search': WebSearchFormatter(),
            'search': WebSearchFormatter(),
            'financial': FinancialFormatter(),
            'finance': FinancialFormatter(),
            'cryptocurrency': FinancialFormatter(),
            'currency': FinancialFormatter(),
            'mutual_fund': FinancialFormatter(),
            'railway': RailwayFormatter(),
            'train': RailwayFormatter(),
            'pnr': RailwayFormatter(),
            'entertainment': EntertainmentFormatter(),
            'joke': EntertainmentFormatter(),
            'quote': EntertainmentFormatter(),
            'dog': EntertainmentFormatter(),
            'cat': EntertainmentFormatter(),
            'default': DefaultFormatter()
        }
        
        logger.info(f"Formatter factory initialized with {len(self.formatters)} formatters")
    
    def get_formatter(self, data_type: str) -> ResponseFormatter:
        """
        Get appropriate formatter for data type.
        
        Args:
            data_type: Type of data to format
            
        Returns:
            Appropriate formatter instance
        """
        data_type_lower = data_type.lower()
        
        # Direct match
        if data_type_lower in self.formatters:
            logger.debug(f"Using {data_type_lower} formatter")
            return self.formatters[data_type_lower]
        
        # Partial matches
        for formatter_type, formatter in self.formatters.items():
            if formatter_type in data_type_lower or data_type_lower in formatter_type:
                logger.debug(f"Using {formatter_type} formatter for {data_type}")
                return formatter
        
        # Default fallback
        logger.debug(f"Using default formatter for {data_type}")
        return self.formatters['default']
    
    def format_data(self, data: Dict[str, Any], data_type: str) -> str:
        """
        Format data using appropriate formatter.
        
        Args:
            data: Data to format
            data_type: Type of data
            
        Returns:
            Formatted string
        """
        try:
            formatter = self.get_formatter(data_type)
            return formatter.format(data)
        except Exception as e:
            logger.error(f"Formatting failed for {data_type}: {e}")
            # Fallback to default formatter
            try:
                return self.formatters['default'].format(data)
            except Exception as fallback_error:
                logger.error(f"Default formatting also failed: {fallback_error}")
                return f"Error formatting {data_type} data: {str(e)}"
    
    def register_formatter(self, data_type: str, formatter: ResponseFormatter):
        """
        Register a new formatter.
        
        Args:
            data_type: Data type identifier
            formatter: Formatter instance
        """
        self.formatters[data_type.lower()] = formatter
        logger.info(f"Registered formatter for {data_type}")
    
    def list_formatters(self) -> list:
        """
        List all available formatter types.
        
        Returns:
            List of formatter type names
        """
        return list(self.formatters.keys())
    
    def format_error(self, error: str, data_type: str = "general") -> str:
        """
        Format error message using appropriate formatter.
        
        Args:
            error: Error message
            data_type: Type of data that caused error
            
        Returns:
            Formatted error message
        """
        try:
            formatter = self.get_formatter(data_type)
            return formatter.format_error(error)
        except Exception:
            # Ultimate fallback
            return f"❌ Error: {error}"
    
    def auto_detect_type(self, data: Dict[str, Any]) -> str:
        """
        Auto-detect data type from data structure.
        
        Args:
            data: Data to analyze
            
        Returns:
            Detected data type
        """
        if not isinstance(data, dict):
            return 'default'
        
        # Check for specific data patterns
        if 'query' in data and ('scraped_content' in data or 'search_results' in data):
            return 'web_search'
        
        if 'cryptocurrency' in data or 'currency_rates' in data or 'mutual_funds' in data:
            return 'financial'
        
        if 'train_number' in data or 'pnr' in data or 'popular_trains' in data:
            return 'railway'
        
        if 'content' in data and 'type' in data:
            content_type = data['type']
            if content_type in ['joke', 'quote', 'dog', 'cat']:
                return 'entertainment'
        
        # Check for entertainment patterns
        if any(key in data for key in ['joke', 'setup', 'punchline', 'quote', 'author', 'image_url', 'fact']):
            return 'entertainment'
        
        return 'default'
    
    def smart_format(self, data: Dict[str, Any], hint: Optional[str] = None) -> str:
        """
        Smart format with auto-detection.
        
        Args:
            data: Data to format
            hint: Optional type hint
            
        Returns:
            Formatted string
        """
        # Use hint if provided, otherwise auto-detect
        data_type = hint if hint else self.auto_detect_type(data)
        
        return self.format_data(data, data_type)


# Singleton instance
_formatter_factory = None

def get_formatter_factory() -> FormatterFactory:
    """Get or create formatter factory instance"""
    global _formatter_factory
    if _formatter_factory is None:
        _formatter_factory = FormatterFactory()
    return _formatter_factory