"""
Response formatters for different data types.
Implements Strategy pattern for consistent formatting.
"""

from .base_formatter import ResponseFormatter
from .web_search_formatter import WebSearchFormatter
from .financial_formatter import FinancialFormatter
from .railway_formatter import RailwayFormatter
from .entertainment_formatter import EntertainmentFormatter
from .formatter_factory import FormatterFactory

__all__ = [
    'ResponseFormatter',
    'WebSearchFormatter',
    'FinancialFormatter',
    'RailwayFormatter',
    'EntertainmentFormatter',
    'FormatterFactory'
]