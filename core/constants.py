"""
Constants and configuration values for Jarvis AI system.
Centralizes magic numbers and thresholds for better maintainability.
"""

from enum import Enum
from typing import Dict, Any


class ResponseLimits:
    """Response formatting and content limits"""
    MAX_CONTENT_LENGTH = 1500
    MAX_SEARCH_RESULTS = 3
    MAX_HISTORY_ITEMS = 10
    MAX_CONVERSATION_TURNS = 5
    MAX_SCRAPED_PAGES = 3
    MAX_NEWS_ITEMS = 5
    MAX_QUERY_LENGTH = 1000
    MIN_QUERY_LENGTH = 1


class ConfidenceThresholds:
    """Confidence thresholds for decision making"""
    CLARIFICATION_NEEDED = 0.4
    LOW_CONFIDENCE = 0.5
    MEDIUM_CONFIDENCE = 0.7
    HIGH_CONFIDENCE = 0.8
    VERY_HIGH_CONFIDENCE = 0.95
    
    # Intent-specific thresholds
    CONVERSATIONAL_THRESHOLD = 0.7
    API_ROUTING_THRESHOLD = 0.8
    WEB_SEARCH_THRESHOLD = 0.6


class CacheSettings:
    """Cache configuration"""
    DEFAULT_TTL = 3600  # 1 hour
    WEB_SEARCH_TTL = 1800  # 30 minutes
    WEATHER_TTL = 600  # 10 minutes
    NEWS_TTL = 300  # 5 minutes
    FINANCIAL_TTL = 60  # 1 minute
    MAX_CACHE_SIZE = 1000


class ModelSettings:
    """Model and AI configuration"""
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 200
    DEFAULT_MODEL = "facebook/blenderbot-400M-distill"
    SPACY_MODEL = "en_core_web_sm"
    
    # Embedding settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384


class APISettings:
    """API configuration and limits"""
    REQUEST_TIMEOUT = 10.0
    MAX_RETRIES = 3
    RATE_LIMIT_DELAY = 1.0
    
    # Indian API specific
    INDIAN_API_TIMEOUT = 15.0
    CRYPTO_API_TIMEOUT = 5.0


class IntentCategories:
    """Intent category mappings"""
    CONVERSATIONAL = "conversational"
    QUESTION = "question"
    COMMAND = "command"
    MATH = "math"
    CODE = "code"
    FETCH = "fetch"
    VISION = "vision"
    LEARNING = "learning"
    UTILITY = "utility"


class ResponseFormats:
    """Response formatting templates"""
    HEADER_SEPARATOR = "=" * 80
    SECTION_SEPARATOR = "-" * 80
    SUBSECTION_SEPARATOR = "─" * 80
    
    # Emoji mappings
    EMOJIS = {
        'search': '🔍',
        'finance': '💰',
        'railway': '🚂',
        'entertainment': '😄',
        'weather': '🌤️',
        'news': '📰',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'magic': '✨',
        'brain': '🧠',
        'robot': '🤖'
    }


class PersonalitySettings:
    """Personality and tone configuration"""
    DEFAULT_PERSONALITY = "magical"
    TONE_ADJUSTMENT_THRESHOLD = 0.3
    
    TONE_MODIFIERS = {
        'excited': ['Amazing!', 'Fantastic!', 'Wow!', '🎉'],
        'encouraging': ['You can do it!', 'Keep going!', 'Great progress!'],
        'celebratory': ['Excellent work!', 'Perfect!', 'Outstanding!'],
        'supportive': ["I'm here to help!", "Let's figure this out!", "We've got this!"],
        'professional': ['Certainly', 'Of course', 'Absolutely', 'Indeed']
    }


class MemorySettings:
    """Memory and learning configuration"""
    MAX_CONVERSATION_HISTORY = 50
    MAX_CONTEXT_TURNS = 3
    LEARNING_CONFIDENCE_THRESHOLD = 0.8
    PREFERENCE_REINFORCEMENT_COUNT = 3
    
    # Topic continuity
    TOPIC_SIMILARITY_THRESHOLD = 0.7
    MAX_TOPIC_HISTORY = 10


class ErrorMessages:
    """Standard error messages"""
    GENERIC_ERROR = "I encountered an error while processing your request."
    TIMEOUT_ERROR = "The request timed out. Please try again."
    NETWORK_ERROR = "I'm having trouble connecting to external services."
    INVALID_INPUT = "I didn't understand that input. Could you rephrase?"
    CLARIFICATION_NEEDED = "I need more information to help you properly."
    SERVICE_UNAVAILABLE = "That service is currently unavailable."


class LoggingSettings:
    """Logging configuration"""
    DEFAULT_LEVEL = "INFO"
    MAX_LOG_SIZE_MB = 10
    RETENTION_DAYS = 7
    
    # Sensitive data patterns to redact
    SENSITIVE_PATTERNS = [
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit cards
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
    ]


# Feature flags for enabling/disabling functionality
class FeatureFlags:
    """Feature toggles for different capabilities"""
    ENABLE_WEB_SCRAPING = True
    ENABLE_INDIAN_APIS = True
    ENABLE_VISION = True
    ENABLE_VOICE = False
    ENABLE_CACHING = True
    ENABLE_METRICS = True
    ENABLE_LEARNING = True
    ENABLE_SENTIMENT_ANALYSIS = True
    ENABLE_TOPIC_MODELING = True


# Default configuration
DEFAULT_CONFIG = {
    'response_limits': ResponseLimits,
    'confidence_thresholds': ConfidenceThresholds,
    'cache_settings': CacheSettings,
    'model_settings': ModelSettings,
    'api_settings': APISettings,
    'personality_settings': PersonalitySettings,
    'memory_settings': MemorySettings,
    'logging_settings': LoggingSettings,
    'feature_flags': FeatureFlags
}