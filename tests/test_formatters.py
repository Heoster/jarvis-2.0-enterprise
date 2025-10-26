"""
Unit tests for Response Formatters.
Tests the Strategy pattern implementation for response formatting.
"""

import pytest
from core.formatters import (
    FormatterFactory,
    WebSearchFormatter,
    FinancialFormatter,
    RailwayFormatter,
    EntertainmentFormatter
)


class TestFormatterFactory:
    """Test cases for FormatterFactory"""
    
    @pytest.fixture
    def factory(self):
        """Create factory instance for testing"""
        return FormatterFactory()
    
    def test_factory_initialization(self, factory):
        """Test factory initializes with correct formatters"""
        assert 'web_search' in factory.formatters
        assert 'financial' in factory.formatters
        assert 'railway' in factory.formatters
        assert 'entertainment' in factory.formatters
        assert 'default' in factory.formatters
    
    def test_get_formatter_direct_match(self, factory):
        """Test getting formatter with direct match"""
        formatter = factory.get_formatter('web_search')
        assert isinstance(formatter, WebSearchFormatter)
    
    def test_get_formatter_partial_match(self, factory):
        """Test getting formatter with partial match"""
        formatter = factory.get_formatter('search_results')
        assert isinstance(formatter, WebSearchFormatter)
    
    def test_get_formatter_fallback(self, factory):
        """Test fallback to default formatter"""
        formatter = factory.get_formatter('unknown_type')
        assert formatter == factory.formatters['default']
    
    def test_auto_detect_web_search(self, factory):
        """Test auto-detection of web search data"""
        data = {
            'query': 'test query',
            'scraped_content': [{'title': 'Test', 'content': 'Content'}]
        }
        
        detected_type = factory.auto_detect_type(data)
        assert detected_type == 'web_search'
    
    def test_auto_detect_financial(self, factory):
        """Test auto-detection of financial data"""
        data = {
            'cryptocurrency': {'price_inr': 1000000},
            'currency_rates': {'USD': 0.012}
        }
        
        detected_type = factory.auto_detect_type(data)
        assert detected_type == 'financial'
    
    def test_auto_detect_railway(self, factory):
        """Test auto-detection of railway data"""
        data = {
            'train_number': '12345',
            'train_name': 'Express Train'
        }
        
        detected_type = factory.auto_detect_type(data)
        assert detected_type == 'railway'
    
    def test_smart_format(self, factory):
        """Test smart formatting with auto-detection"""
        data = {
            'query': 'test',
            'search_results': [{'title': 'Result'}]
        }
        
        formatted = factory.smart_format(data)
        assert 'SEARCH RESULTS' in formatted.upper()
    
    def test_register_custom_formatter(self, factory):
        """Test registering custom formatter"""
        class CustomFormatter:
            def format(self, data):
                return "Custom formatted"
        
        custom_formatter = CustomFormatter()
        factory.register_formatter('custom', custom_formatter)
        
        assert 'custom' in factory.formatters
        assert factory.formatters['custom'] == custom_formatter


class TestWebSearchFormatter:
    """Test cases for WebSearchFormatter"""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance for testing"""
        return WebSearchFormatter()
    
    def test_format_scraped_content(self, formatter):
        """Test formatting scraped content"""
        data = {
            'query': 'test query',
            'scraped_content': [
                {
                    'title': 'Test Article',
                    'url': 'https://example.com/test',
                    'snippet': 'Test snippet',
                    'content': 'Test content with more details'
                }
            ]
        }
        
        formatted = formatter.format(data)
        
        assert 'SEARCH RESULTS' in formatted.upper()
        assert 'test query' in formatted.lower()
        assert 'Test Article' in formatted
        assert 'example.com' in formatted
    
    def test_format_search_results_only(self, formatter):
        """Test formatting search results without scraped content"""
        data = {
            'query': 'test query',
            'search_results': [
                {
                    'title': 'Search Result',
                    'url': 'https://example.com',
                    'snippet': 'Result snippet'
                }
            ]
        }
        
        formatted = formatter.format(data)
        
        assert 'Found 1 search results' in formatted
        assert 'Search Result' in formatted
    
    def test_format_no_results(self, formatter):
        """Test formatting when no results found"""
        data = {
            'query': 'test query',
            'scraped_content': [],
            'search_results': []
        }
        
        formatted = formatter.format(data)
        
        assert 'No results found' in formatted
    
    def test_extract_domain(self, formatter):
        """Test domain extraction from URL"""
        url = 'https://www.example.com/path/to/page'
        domain = formatter.extract_domain(url)
        assert domain == 'example.com'
    
    def test_format_search_error(self, formatter):
        """Test formatting search error"""
        error_msg = formatter.format_search_error('test query', 'Network error')
        
        assert 'Search Error' in error_msg
        assert 'test query' in error_msg
        assert 'Network error' in error_msg


class TestFinancialFormatter:
    """Test cases for FinancialFormatter"""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance for testing"""
        return FinancialFormatter()
    
    def test_format_cryptocurrency(self, formatter):
        """Test formatting cryptocurrency data"""
        data = {
            'cryptocurrency': {
                'price_inr': 2500000.50,
                'price_usd': 30000.00,
                'updated': '2024-01-01T12:00:00Z'
            }
        }
        
        formatted = formatter.format(data)
        
        assert 'CRYPTOCURRENCY PRICES' in formatted.upper()
        assert '₹2,500,000.50' in formatted
        assert '$30,000.00' in formatted
    
    def test_format_currency_rates(self, formatter):
        """Test formatting currency rates"""
        data = {
            'currency_rates': {
                'rates': {
                    'USD': 0.012,
                    'EUR': 0.011,
                    'GBP': 0.009
                },
                'updated': '2024-01-01T12:00:00Z'
            }
        }
        
        formatted = formatter.format(data)
        
        assert 'CURRENCY EXCHANGE RATES' in formatted.upper()
        assert 'USD' in formatted
        assert '0.012' in formatted
    
    def test_format_mutual_funds(self, formatter):
        """Test formatting mutual fund data"""
        data = {
            'scheme_name': 'SBI BlueChip Fund',
            'scheme_code': '123456',
            'nav': 45.67,
            'fund_house': 'SBI Mutual Fund'
        }
        
        formatted = formatter._format_single_fund(data)
        
        assert 'SBI BlueChip Fund' in formatted
        assert '123456' in formatted
        assert '45.67' in formatted
    
    def test_format_no_data(self, formatter):
        """Test formatting when no financial data available"""
        data = {}
        
        formatted = formatter.format(data)
        
        assert 'No financial data available' in formatted


class TestRailwayFormatter:
    """Test cases for RailwayFormatter"""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance for testing"""
        return RailwayFormatter()
    
    def test_format_train_details(self, formatter):
        """Test formatting train details"""
        data = {
            'train_number': '12345',
            'train_name': 'Express Train',
            'route': 'Delhi - Mumbai',
            'departure_time': '08:00',
            'arrival_time': '20:00'
        }
        
        formatted = formatter.format(data)
        
        assert 'TRAIN DETAILS' in formatted.upper()
        assert '12345' in formatted
        assert 'Express Train' in formatted
        assert 'Delhi - Mumbai' in formatted
    
    def test_format_popular_trains(self, formatter):
        """Test formatting popular trains list"""
        data = {
            'popular_trains_from_muzaffarnagar': [
                '12345 - Express Train',
                '67890 - Passenger Train'
            ]
        }
        
        formatted = formatter.format(data)
        
        assert 'POPULAR TRAINS' in formatted.upper()
        assert '12345' in formatted
        assert '67890' in formatted
    
    def test_format_railway_error(self, formatter):
        """Test formatting railway error"""
        error_msg = formatter.format_railway_error('Connection failed', 'train_info')
        
        assert 'Train_Info Error' in error_msg
        assert 'Connection failed' in error_msg
        assert 'Suggestions' in error_msg


class TestEntertainmentFormatter:
    """Test cases for EntertainmentFormatter"""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance for testing"""
        return EntertainmentFormatter()
    
    def test_format_joke(self, formatter):
        """Test formatting joke content"""
        data = {
            'content': {
                'setup': 'Why did the programmer quit?',
                'punchline': 'Because they didn\'t get arrays!',
                'type': 'programming'
            },
            'type': 'joke'
        }
        
        formatted = formatter.format(data)
        
        assert 'RANDOM JOKE' in formatted.upper()
        assert 'Why did the programmer quit?' in formatted
        assert 'Because they didn\'t get arrays!' in formatted
    
    def test_format_quote(self, formatter):
        """Test formatting quote content"""
        data = {
            'content': {
                'quote': 'The only way to do great work is to love what you do.',
                'author': 'Steve Jobs'
            },
            'type': 'quote'
        }
        
        formatted = formatter.format(data)
        
        assert 'INSPIRATIONAL QUOTE' in formatted.upper()
        assert 'The only way to do great work' in formatted
        assert 'Steve Jobs' in formatted
    
    def test_format_dog_image(self, formatter):
        """Test formatting dog image content"""
        data = {
            'content': {
                'image_url': 'https://example.com/dog.jpg'
            },
            'type': 'dog'
        }
        
        formatted = formatter.format(data)
        
        assert 'RANDOM DOG IMAGE' in formatted.upper()
        assert 'https://example.com/dog.jpg' in formatted
        assert 'Fun Fact' in formatted
    
    def test_format_entertainment_error(self, formatter):
        """Test formatting entertainment error"""
        error_msg = formatter.format_entertainment_error('API unavailable', 'joke')
        
        assert 'Joke Error' in error_msg
        assert 'API unavailable' in error_msg
        assert 'Suggestions' in error_msg


if __name__ == "__main__":
    pytest.main([__file__])