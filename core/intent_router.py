"""
Centralized intent routing with priority-based decision making.
Implements Chain of Responsibility pattern for query routing.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime

from core.models import Intent, IntentCategory
from core.logger import get_logger
from core.constants import ConfidenceThresholds, IntentCategories
from core.conversation_handler import get_conversation_handler
from core.api_router import get_api_router
from core.web_scraper import get_web_scraper
from core.indian_apis import get_indian_api
from execution.math_engine import MathEngine

logger = get_logger(__name__)


class RouteHandler:
    """Base class for route handlers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"RouteHandler.{name}")
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if this handler can process the query"""
        return False
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Handle the query and return response"""
        raise NotImplementedError


class ClarificationHandler(RouteHandler):
    """Handle clarification requests"""
    
    def __init__(self):
        super().__init__("Clarification")
        self.conversation_handler = get_conversation_handler()
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if clarification is needed"""
        return (
            intent.confidence < ConfidenceThresholds.CLARIFICATION_NEEDED or
            context.get('needs_clarification', False) or
            self.conversation_handler.should_ask_clarification(query, {'intent': intent.category.value, 'confidence': intent.confidence})
        )
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Generate clarification question"""
        understanding = {'intent': intent.category.value, 'confidence': intent.confidence}
        is_ambiguous, options = self.conversation_handler.detect_ambiguity(query, understanding)
        
        if is_ambiguous:
            if not options or options == ['Please be more specific about what you need']:
                options = self.conversation_handler.generate_suggestions(query)
            
            clarification = self.conversation_handler.generate_clarification_question(query, options)
            self.conversation_handler.awaiting_clarification = True
            self.conversation_handler.clarification_options = options
            
            return clarification
        
        return "I need more information to help you properly. Could you please be more specific?"


class ConversationalHandler(RouteHandler):
    """Handle conversational intents (greetings, thanks, etc.)"""
    
    def __init__(self):
        super().__init__("Conversational")
        self.conversation_handler = get_conversation_handler()
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if this is a conversational query"""
        conversational_intents = ['greeting', 'farewell', 'thanks', 'how_are_you', 'who_are_you', 'what_can_you_do']
        
        # Check if conversation handler detected conversational intent
        understanding = self.conversation_handler.understand_query(query)
        detected_intent = understanding.get('intent')
        
        return (
            detected_intent in conversational_intents or
            intent.category == IntentCategory.CONVERSATIONAL or
            (intent.confidence > ConfidenceThresholds.CONVERSATIONAL_THRESHOLD and 
             detected_intent in conversational_intents)
        )
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Generate conversational response"""
        understanding = self.conversation_handler.understand_query(query)
        response = self.conversation_handler.generate_contextual_response(query, understanding)
        
        if response:
            self.conversation_handler.add_to_history(query, response, understanding.get('intent'))
            return response
        
        # Fallback conversational response
        return "I'm here to help! What can I do for you today?"


class APIHandler(RouteHandler):
    """Handle API endpoint routing"""
    
    def __init__(self):
        super().__init__("API")
        self.api_router = get_api_router()
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if query should be routed to API"""
        # Check for explicit API commands
        api_keywords = ['correct', 'fix', 'grammar', 'quiz', 'test', 'feedback', 'rate', 'magic']
        query_lower = query.lower()
        
        return (
            any(keyword in query_lower for keyword in api_keywords) or
            query_lower.startswith('/') or  # Explicit commands
            context.get('active_quiz_id') is not None
        )
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Route to appropriate API endpoint"""
        api_context = {
            'active_quiz_id': context.get('active_quiz_id'),
            'last_query': context.get('last_query'),
            'last_response': context.get('last_response')
        }
        
        api_result = await self.api_router.route_request(query, api_context)
        
        if api_result.get('routed'):
            return api_result.get('formatted', 'Request processed.')
        
        return "I couldn't process that as an API request. Please try a different approach."


class IndianAPIHandler(RouteHandler):
    """Handle Indian-specific API queries"""
    
    def __init__(self):
        super().__init__("IndianAPI")
        self.indian_api = None
    
    async def _ensure_api(self):
        """Ensure Indian API is initialized"""
        if self.indian_api is None:
            self.indian_api = await get_indian_api()
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if query needs Indian-specific data"""
        query_lower = query.lower()
        
        # Financial keywords
        financial_keywords = ['bitcoin', 'crypto', 'btc', 'currency', 'exchange rate', 'inr', 'rupee']
        # Railway keywords
        railway_keywords = ['train', 'railway', 'pnr', 'irctc', 'train schedule']
        # Mutual fund keywords
        mf_keywords = ['mutual fund', 'nav', 'sbi bluechip', 'hdfc', 'icici', 'scheme code']
        # Entertainment keywords
        entertainment_keywords = ['joke', 'funny', 'dog image', 'cat fact', 'quote', 'inspire me']
        # Location keywords
        location_keywords = ['muzaffarnagar', 'pincode', 'pin code', '251201', 'uttar pradesh', 'my location']
        
        return (
            any(keyword in query_lower for keyword in financial_keywords) or
            any(keyword in query_lower for keyword in railway_keywords) or
            any(keyword in query_lower for keyword in mf_keywords) or
            any(keyword in query_lower for keyword in entertainment_keywords) or
            any(keyword in query_lower for keyword in location_keywords)
        )
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Handle Indian API queries"""
        await self._ensure_api()
        query_lower = query.lower()
        
        # Determine query type and fetch appropriate data
        if any(keyword in query_lower for keyword in ['train', 'railway', 'pnr', 'irctc']):
            railway_data = await self.indian_api.get_railway_info()
            if not railway_data.get('error'):
                return self._format_railway_data(railway_data)
        
        elif any(keyword in query_lower for keyword in ['mutual fund', 'nav']):
            mf_data = await self.indian_api.get_mutual_fund_info()
            if not mf_data.get('error'):
                return self._format_mutual_fund_data(mf_data)
        
        elif any(keyword in query_lower for keyword in ['joke', 'funny', 'dog', 'cat', 'quote', 'inspire']):
            content_type = self._determine_entertainment_type(query_lower)
            entertainment_data = await self.indian_api.get_entertainment(content_type)
            if not entertainment_data.get('error'):
                return self._format_entertainment_data(entertainment_data, content_type)
        
        elif any(keyword in query_lower for keyword in ['bitcoin', 'crypto', 'currency', 'exchange']):
            financial_data = await self.indian_api.get_financial_summary()
            if not financial_data.get('error'):
                return self._format_financial_data(financial_data)
        
        elif any(keyword in query_lower for keyword in ['muzaffarnagar', 'pincode', 'location']):
            location_data = await self.indian_api.get_location_summary()
            if not location_data.get('error'):
                return self._format_location_data(location_data)
        
        return "I couldn't retrieve the requested Indian data. Please try again later."
    
    def _determine_entertainment_type(self, query_lower: str) -> str:
        """Determine entertainment content type"""
        if 'programming' in query_lower or 'code' in query_lower:
            return 'programming_joke'
        elif 'dog' in query_lower:
            return 'dog'
        elif 'cat' in query_lower:
            return 'cat'
        elif 'quote' in query_lower or 'inspire' in query_lower:
            return 'quote'
        else:
            return 'joke'
    
    def _format_railway_data(self, data: Dict[str, Any]) -> str:
        """Format railway data"""
        # Use formatter when available
        from core.formatters.railway_formatter import RailwayFormatter
        formatter = RailwayFormatter()
        return formatter.format(data)
    
    def _format_mutual_fund_data(self, data: Dict[str, Any]) -> str:
        """Format mutual fund data"""
        from core.formatters.financial_formatter import FinancialFormatter
        formatter = FinancialFormatter()
        return formatter._format_mutual_funds(data)
    
    def _format_entertainment_data(self, data: Dict[str, Any], content_type: str) -> str:
        """Format entertainment data"""
        from core.formatters.entertainment_formatter import EntertainmentFormatter
        formatter = EntertainmentFormatter()
        return formatter.format({'content': data, 'type': content_type})
    
    def _format_financial_data(self, data: Dict[str, Any]) -> str:
        """Format financial data"""
        from core.formatters.financial_formatter import FinancialFormatter
        formatter = FinancialFormatter()
        return formatter.format(data)
    
    def _format_location_data(self, data: Dict[str, Any]) -> str:
        """Format location data"""
        # Simple formatting for now
        response = "📍 Location Information:\n\n"
        if 'pincode_info' in data:
            pincode = data['pincode_info']
            response += f"PIN Code: {pincode.get('pincode', 'N/A')}\n"
            response += f"Place: {pincode.get('place_name', 'N/A')}\n"
            response += f"State: {pincode.get('state', 'N/A')}\n"
        return response


class WebSearchHandler(RouteHandler):
    """Handle web search queries"""
    
    def __init__(self):
        super().__init__("WebSearch")
        self.web_scraper = None
    
    async def _ensure_scraper(self):
        """Ensure web scraper is initialized"""
        if self.web_scraper is None:
            self.web_scraper = await get_web_scraper()
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if query needs web search"""
        search_keywords = ['search', 'find', 'look up', 'what is', 'who is', 'latest', 'news about', 'information on', 'tell me about']
        query_lower = query.lower()
        
        return (
            any(keyword in query_lower for keyword in search_keywords) and
            not context.get('skip_web_search', False) and
            intent.category in [IntentCategory.QUESTION, IntentCategory.FETCH]
        )
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Handle web search query"""
        await self._ensure_scraper()
        
        # Extract search query
        search_query = self._extract_search_query(query)
        
        # Perform search and scrape
        web_results = await self.web_scraper.search_and_scrape(search_query, num_results=3)
        
        if web_results and not web_results.get('error') and web_results.get('scraped_content'):
            from core.formatters.web_search_formatter import WebSearchFormatter
            formatter = WebSearchFormatter()
            return formatter.format(web_results)
        
        return f"I couldn't find reliable information about '{search_query}'. Please try a different search term."
    
    def _extract_search_query(self, query: str) -> str:
        """Extract search query from user input"""
        search_keywords = ['search for', 'find', 'look up', 'what is', 'who is', 'tell me about', 'information on']
        
        query_lower = query.lower()
        for keyword in search_keywords:
            if keyword in query_lower:
                search_query = query_lower.split(keyword)[-1].strip()
                return search_query if search_query else query
        
        return query


class ExecutionHandler(RouteHandler):
    """Handle execution queries (math, code, etc.)"""
    
    def __init__(self):
        super().__init__("Execution")
        self.math_engine = MathEngine()
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """Check if query needs execution"""
        return (
            intent.category == IntentCategory.MATH or
            context.get('needs_execution', False) or
            any(word in query.lower() for word in ['calculate', 'compute', 'solve', '+', '-', '*', '/'])
        )
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Handle execution query"""
        if intent.category == IntentCategory.MATH:
            # Extract mathematical expression
            expression = self._extract_math_expression(query)
            result = await self.math_engine.evaluate(expression)
            
            if result.get('success'):
                return f"The calculation yields: {result['result']}"
            else:
                return f"I couldn't solve that mathematical expression: {result.get('error', 'Unknown error')}"
        
        return "I can help with mathematical calculations. Please provide a clear expression."
    
    def _extract_math_expression(self, query: str) -> str:
        """Extract mathematical expression from query"""
        # Simple extraction - can be enhanced
        math_keywords = ['calculate', 'compute', 'solve', 'what is']
        
        query_lower = query.lower()
        for keyword in math_keywords:
            if keyword in query_lower:
                expression = query_lower.split(keyword)[-1].strip()
                return expression if expression else query
        
        return query


class AIGenerationHandler(RouteHandler):
    """Fallback handler for AI generation"""
    
    def __init__(self):
        super().__init__("AIGeneration")
    
    async def can_handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> bool:
        """This handler can always handle queries as fallback"""
        return True
    
    async def handle(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Generate AI response as fallback"""
        # This would integrate with the main AI generation system
        # For now, return a helpful fallback
        return "I understand you're asking about something, but I need more specific information to provide the best help. Could you please rephrase your question or provide more details?"


class IntentRouter:
    """
    Centralized intent routing with priority-based decision making.
    Implements Chain of Responsibility pattern.
    """
    
    def __init__(self):
        """Initialize router with handlers in priority order"""
        self.handlers: List[RouteHandler] = [
            ClarificationHandler(),
            ConversationalHandler(),
            APIHandler(),
            IndianAPIHandler(),
            WebSearchHandler(),
            ExecutionHandler(),
            AIGenerationHandler()  # Always last as fallback
        ]
        self.logger = get_logger(__name__)
        self.metrics = {
            'total_routes': 0,
            'handler_usage': {handler.name: 0 for handler in self.handlers}
        }
    
    async def route(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """
        Route query through priority chain.
        
        Args:
            query: User query
            intent: Classified intent
            context: Additional context
            
        Returns:
            Response string
        """
        self.metrics['total_routes'] += 1
        start_time = datetime.now()
        
        self.logger.info(f"Routing query: {query[:50]}... (Intent: {intent.category.value}, Confidence: {intent.confidence:.2f})")
        
        # Try each handler in priority order
        for handler in self.handlers:
            try:
                if await handler.can_handle(query, intent, context):
                    self.logger.info(f"Routing to: {handler.name}")
                    self.metrics['handler_usage'][handler.name] += 1
                    
                    response = await handler.handle(query, intent, context)
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    self.logger.info(f"Route completed by {handler.name} in {execution_time:.2f}s")
                    
                    return response
                    
            except Exception as e:
                self.logger.error(f"Handler {handler.name} failed: {e}")
                continue
        
        # Should never reach here due to AIGenerationHandler fallback
        self.logger.error("No handler could process the query")
        return "I'm sorry, I couldn't process your request. Please try again."
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics"""
        return {
            'total_routes': self.metrics['total_routes'],
            'handler_usage': self.metrics['handler_usage'].copy(),
            'handlers': [handler.name for handler in self.handlers]
        }
    
    def add_handler(self, handler: RouteHandler, position: Optional[int] = None):
        """
        Add a new handler to the chain.
        
        Args:
            handler: Handler to add
            position: Position in chain (None = before fallback)
        """
        if position is None:
            # Insert before the last handler (AIGenerationHandler)
            position = len(self.handlers) - 1
        
        self.handlers.insert(position, handler)
        self.metrics['handler_usage'][handler.name] = 0
        self.logger.info(f"Added handler {handler.name} at position {position}")
    
    def remove_handler(self, handler_name: str) -> bool:
        """
        Remove a handler from the chain.
        
        Args:
            handler_name: Name of handler to remove
            
        Returns:
            True if handler was removed
        """
        for i, handler in enumerate(self.handlers):
            if handler.name == handler_name:
                # Don't allow removing the fallback handler
                if handler_name != "AIGeneration":
                    self.handlers.pop(i)
                    del self.metrics['handler_usage'][handler_name]
                    self.logger.info(f"Removed handler {handler_name}")
                    return True
                else:
                    self.logger.warning("Cannot remove fallback AIGeneration handler")
                    return False
        
        self.logger.warning(f"Handler {handler_name} not found")
        return False


# Singleton instance
_intent_router = None

def get_intent_router() -> IntentRouter:
    """Get or create intent router instance"""
    global _intent_router
    if _intent_router is None:
        _intent_router = IntentRouter()
    return _intent_router