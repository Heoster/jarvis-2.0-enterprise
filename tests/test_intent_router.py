"""
Unit tests for Intent Router system.
Tests the centralized routing logic and handlers.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from core.intent_router import (
    IntentRouter, 
    ClarificationHandler,
    ConversationalHandler,
    APIHandler,
    IndianAPIHandler,
    WebSearchHandler,
    ExecutionHandler,
    AIGenerationHandler
)
from core.models import Intent, IntentCategory


class TestIntentRouter:
    """Test cases for IntentRouter"""
    
    @pytest.fixture
    def router(self):
        """Create router instance for testing"""
        return IntentRouter()
    
    @pytest.fixture
    def sample_intent(self):
        """Create sample intent for testing"""
        return Intent(
            category=IntentCategory.QUESTION,
            confidence=0.8,
            parameters={},
            context={}
        )
    
    @pytest.mark.asyncio
    async def test_router_initialization(self, router):
        """Test router initializes with correct handlers"""
        assert len(router.handlers) == 7
        assert isinstance(router.handlers[0], ClarificationHandler)
        assert isinstance(router.handlers[-1], AIGenerationHandler)
    
    @pytest.mark.asyncio
    async def test_conversational_routing(self, router, sample_intent):
        """Test routing of conversational queries"""
        query = "hello jarvis"
        context = {}
        
        with patch.object(router.handlers[1], 'can_handle', return_value=True):
            with patch.object(router.handlers[1], 'handle', return_value="Hello! How can I help?"):
                response = await router.route(query, sample_intent, context)
                assert "Hello" in response
    
    @pytest.mark.asyncio
    async def test_clarification_routing(self, router):
        """Test routing when clarification is needed"""
        query = "help"
        low_confidence_intent = Intent(
            category=IntentCategory.QUESTION,
            confidence=0.2,  # Low confidence
            parameters={},
            context={}
        )
        context = {}
        
        with patch.object(router.handlers[0], 'can_handle', return_value=True):
            with patch.object(router.handlers[0], 'handle', return_value="I need more information"):
                response = await router.route(query, low_confidence_intent, context)
                assert "more information" in response.lower()
    
    @pytest.mark.asyncio
    async def test_fallback_to_ai_generation(self, router, sample_intent):
        """Test fallback to AI generation handler"""
        query = "complex query that no handler can process"
        context = {}
        
        # Mock all handlers except the last one to return False for can_handle
        for handler in router.handlers[:-1]:
            handler.can_handle = AsyncMock(return_value=False)
        
        # Mock the AI generation handler
        router.handlers[-1].handle = AsyncMock(return_value="AI generated response")
        
        response = await router.route(query, sample_intent, context)
        assert response == "AI generated response"
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, router, sample_intent):
        """Test that metrics are collected during routing"""
        query = "test query"
        context = {}
        
        initial_routes = router.metrics['total_routes']
        
        with patch.object(router.handlers[-1], 'handle', return_value="response"):
            await router.route(query, sample_intent, context)
        
        assert router.metrics['total_routes'] == initial_routes + 1
    
    def test_add_handler(self, router):
        """Test adding new handler to router"""
        class TestHandler:
            def __init__(self):
                self.name = "TestHandler"
        
        test_handler = TestHandler()
        initial_count = len(router.handlers)
        
        router.add_handler(test_handler, position=0)
        
        assert len(router.handlers) == initial_count + 1
        assert router.handlers[0] == test_handler
    
    def test_remove_handler(self, router):
        """Test removing handler from router"""
        # Try to remove a handler (not the fallback)
        handler_name = router.handlers[0].name
        initial_count = len(router.handlers)
        
        success = router.remove_handler(handler_name)
        
        assert success
        assert len(router.handlers) == initial_count - 1
    
    def test_cannot_remove_fallback_handler(self, router):
        """Test that fallback handler cannot be removed"""
        success = router.remove_handler("AIGeneration")
        assert not success


class TestClarificationHandler:
    """Test cases for ClarificationHandler"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance for testing"""
        return ClarificationHandler()
    
    @pytest.mark.asyncio
    async def test_can_handle_low_confidence(self, handler):
        """Test handler detects low confidence queries"""
        query = "help"
        intent = Intent(
            category=IntentCategory.QUESTION,
            confidence=0.3,  # Below threshold
            parameters={},
            context={}
        )
        context = {}
        
        can_handle = await handler.can_handle(query, intent, context)
        assert can_handle
    
    @pytest.mark.asyncio
    async def test_can_handle_needs_clarification_flag(self, handler):
        """Test handler detects needs_clarification flag"""
        query = "test"
        intent = Intent(
            category=IntentCategory.QUESTION,
            confidence=0.8,
            parameters={},
            context={}
        )
        context = {'needs_clarification': True}
        
        can_handle = await handler.can_handle(query, intent, context)
        assert can_handle
    
    @pytest.mark.asyncio
    async def test_generate_clarification(self, handler):
        """Test clarification question generation"""
        query = "help"
        intent = Intent(
            category=IntentCategory.QUESTION,
            confidence=0.3,
            parameters={},
            context={}
        )
        context = {}
        
        with patch.object(handler.conversation_handler, 'detect_ambiguity', return_value=(True, ['option1', 'option2'])):
            with patch.object(handler.conversation_handler, 'generate_clarification_question', return_value="Please choose an option"):
                response = await handler.handle(query, intent, context)
                assert "choose" in response.lower()


class TestWebSearchHandler:
    """Test cases for WebSearchHandler"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance for testing"""
        return WebSearchHandler()
    
    @pytest.mark.asyncio
    async def test_can_handle_search_keywords(self, handler):
        """Test handler detects search keywords"""
        query = "search for python tutorials"
        intent = Intent(
            category=IntentCategory.FETCH,
            confidence=0.8,
            parameters={},
            context={}
        )
        context = {}
        
        can_handle = await handler.can_handle(query, intent, context)
        assert can_handle
    
    @pytest.mark.asyncio
    async def test_extract_search_query(self, handler):
        """Test search query extraction"""
        query = "search for machine learning"
        extracted = handler._extract_search_query(query)
        assert "machine learning" in extracted
    
    @pytest.mark.asyncio
    async def test_handle_web_search(self, handler):
        """Test web search handling"""
        query = "find information about AI"
        intent = Intent(
            category=IntentCategory.FETCH,
            confidence=0.8,
            parameters={},
            context={}
        )
        context = {}
        
        # Mock web scraper
        mock_results = {
            'query': 'AI',
            'scraped_content': [
                {'title': 'AI Article', 'content': 'AI content', 'url': 'http://example.com'}
            ]
        }
        
        with patch.object(handler, '_ensure_scraper'):
            with patch.object(handler, 'web_scraper') as mock_scraper:
                mock_scraper.search_and_scrape = AsyncMock(return_value=mock_results)
                
                response = await handler.handle(query, intent, context)
                assert "AI Article" in response


class TestExecutionHandler:
    """Test cases for ExecutionHandler"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance for testing"""
        return ExecutionHandler()
    
    @pytest.mark.asyncio
    async def test_can_handle_math_intent(self, handler):
        """Test handler detects math intents"""
        query = "calculate 2 + 2"
        intent = Intent(
            category=IntentCategory.MATH,
            confidence=0.8,
            parameters={},
            context={}
        )
        context = {}
        
        can_handle = await handler.can_handle(query, intent, context)
        assert can_handle
    
    @pytest.mark.asyncio
    async def test_extract_math_expression(self, handler):
        """Test math expression extraction"""
        query = "calculate 5 * 3"
        expression = handler._extract_math_expression(query)
        assert "5 * 3" in expression
    
    @pytest.mark.asyncio
    async def test_handle_math_execution(self, handler):
        """Test math execution handling"""
        query = "solve 2 + 2"
        intent = Intent(
            category=IntentCategory.MATH,
            confidence=0.8,
            parameters={},
            context={}
        )
        context = {}
        
        # Mock math engine
        mock_result = {'success': True, 'result': 4.0}
        
        with patch.object(handler.math_engine, 'evaluate', return_value=mock_result):
            response = await handler.handle(query, intent, context)
            assert "4" in response


if __name__ == "__main__":
    pytest.main([__file__])