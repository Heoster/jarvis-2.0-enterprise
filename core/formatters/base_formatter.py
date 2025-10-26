"""
Base formatter class implementing Strategy pattern.
All response formatters inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from core.constants import ResponseFormats


class ResponseFormatter(ABC):
    """
    Base formatter for different response types.
    Implements Strategy pattern for consistent formatting.
    """
    
    def __init__(self):
        self.emojis = ResponseFormats.EMOJIS
        self.header_sep = ResponseFormats.HEADER_SEPARATOR
        self.section_sep = ResponseFormats.SECTION_SEPARATOR
        self.subsection_sep = ResponseFormats.SUBSECTION_SEPARATOR
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data into human-readable response.
        
        Args:
            data: Data to format
            
        Returns:
            Formatted response string
        """
        pass
    
    def add_header(self, title: str, emoji: str = "📋") -> str:
        """
        Add formatted header to response.
        
        Args:
            title: Header title
            emoji: Header emoji
            
        Returns:
            Formatted header string
        """
        return f"\n{self.header_sep}\n{emoji} {title.upper()}\n{self.header_sep}\n\n"
    
    def add_section(self, title: str, emoji: str = "📄") -> str:
        """
        Add formatted section header.
        
        Args:
            title: Section title
            emoji: Section emoji
            
        Returns:
            Formatted section header
        """
        return f"{emoji} {title.upper()}\n{self.section_sep}\n"
    
    def add_subsection(self, title: str, index: Optional[int] = None) -> str:
        """
        Add formatted subsection header.
        
        Args:
            title: Subsection title
            index: Optional index number
            
        Returns:
            Formatted subsection header
        """
        if index is not None:
            return f"\n{self.subsection_sep}\n📄 {title.upper()} #{index}\n{self.subsection_sep}\n\n"
        else:
            return f"\n{self.subsection_sep}\n📄 {title.upper()}\n{self.subsection_sep}\n\n"
    
    def add_footer(self, message: str = "", emoji: str = "✅") -> str:
        """
        Add formatted footer to response.
        
        Args:
            message: Footer message
            emoji: Footer emoji
            
        Returns:
            Formatted footer string
        """
        footer = f"\n{self.header_sep}\n"
        if message:
            footer += f"{emoji} {message}\n{self.header_sep}\n"
        return footer
    
    def extract_domain(self, url: str) -> str:
        """
        Extract clean domain name from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Clean domain name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain if domain else 'Unknown'
        except Exception:
            return 'Unknown'
    
    def truncate_text(self, text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    def format_list_items(self, items: list, bullet: str = "•") -> str:
        """
        Format list of items with bullets.
        
        Args:
            items: List of items to format
            bullet: Bullet character
            
        Returns:
            Formatted list string
        """
        if not items:
            return "No items available"
        
        return "\n".join(f"  {bullet} {item}" for item in items)
    
    def format_key_value_pairs(self, data: Dict[str, Any], indent: str = "  ") -> str:
        """
        Format dictionary as key-value pairs.
        
        Args:
            data: Dictionary to format
            indent: Indentation string
            
        Returns:
            Formatted key-value string
        """
        if not data:
            return "No data available"
        
        lines = []
        for key, value in data.items():
            # Format key nicely
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"{indent}{formatted_key}: {value}")
        
        return "\n".join(lines)
    
    def add_metadata_section(self, metadata: Dict[str, Any]) -> str:
        """
        Add formatted metadata section.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Formatted metadata section
        """
        if not metadata:
            return ""
        
        section = f"\n{self.emojis['info']} METADATA\n{self.section_sep}\n"
        section += self.format_key_value_pairs(metadata)
        section += "\n"
        
        return section
    
    def format_error(self, error: str, context: Optional[str] = None) -> str:
        """
        Format error message.
        
        Args:
            error: Error message
            context: Optional context information
            
        Returns:
            Formatted error message
        """
        response = self.add_header("Error", self.emojis['error'])
        response += f"❌ {error}\n"
        
        if context:
            response += f"\nContext: {context}\n"
        
        response += self.add_footer("Please try again or contact support")
        
        return response
    
    def format_no_data(self, message: str = "No data available") -> str:
        """
        Format no data message.
        
        Args:
            message: No data message
            
        Returns:
            Formatted no data message
        """
        response = self.add_header("No Results", self.emojis['warning'])
        response += f"⚠️ {message}\n"
        response += self.add_footer("Try a different query or check back later")
        
        return response