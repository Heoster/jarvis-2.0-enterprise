"""
Intelligent API Router
Automatically selects and calls appropriate API endpoints based on user intent
"""

import re
from typing import Dict, Any, Optional, List
from enum import Enum
import aiohttp
from core.logger import get_logger
from core.codeex_personality import CodeexPersonality

logger = get_logger(__name__)


class APIEndpoint(Enum):
    """Available API endpoints"""
    CORRECT = "correct"
    MAGIC = "magic"
    QUIZ_CREATE = "quiz_create"
    QUIZ_ANSWER = "quiz_answer"
    QUIZ_RESULTS = "quiz_results"
    QUIZ_TOPICS = "quiz_topics"
    QUIZ_STATS = "quiz_stats"
    FEEDBACK = "feedback"
    FEEDBACK_STATS = "feedback_stats"
    FEEDBACK_REPORT = "feedback_report"


class IntelligentAPIRouter:
    """Routes user requests to appropriate API endpoints automatically"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.personality = CodeexPersonality()
        
        # Intent patterns for automatic API selection
        self.intent_patterns = {
            APIEndpoint.CORRECT: [
                r'\b(correct|fix|grammar|spell|check)\b.*\b(sentence|text|writing|grammar)\b',
                r'\b(is this correct|check my)\b',
                r'\bhow do (i|you) (spell|write)\b',
                r'\b(punctuation|capitalization)\b',
            ],
            APIEndpoint.QUIZ_CREATE: [
                r'\b(quiz|test|exam|assessment)\b.*\b(start|create|take|begin)\b',
                r'\b(test my knowledge|quiz me)\b',
                r'\bstart.*\b(quiz|test)\b',
            ],
            APIEndpoint.QUIZ_TOPICS: [
                r'\b(what|which|list).*\b(quiz|test).*\b(topics|subjects|available)\b',
                r'\b(quiz|test).*\b(topics|subjects)\b',
                r'\bshow.*\b(quiz|test).*\b(topics|options)\b',
            ],
            APIEndpoint.QUIZ_STATS: [
                r'\b(my|show).*\b(quiz|test).*\b(stats|statistics|score|progress)\b',
                r'\bhow (am i doing|did i do)\b.*\b(quiz|test)\b',
                r'\b(quiz|test).*\b(performance|results|history)\b',
            ],
            APIEndpoint.FEEDBACK: [
                r'\b(feedback|rate|review)\b',
                r'\b(good|bad|great|poor|excellent|terrible)\b.*\b(response|answer|help)\b',
                r'\bthat (was|is) (helpful|not helpful|good|bad)\b',
            ],
            APIEndpoint.FEEDBACK_STATS: [
                r'\b(feedback|satisfaction).*\b(stats|statistics|rate)\b',
                r'\bhow.*\b(doing|performing)\b.*\b(overall|general)\b',
            ],
            APIEndpoint.MAGIC: [
                r'\b(magic|magical|sparkle|enchant)\b',
                r'\bmake it (fun|magical|special)\b',
            ],
        }
        
        # Keyword triggers for quick detection
        self.keyword_triggers = {
            'correct': APIEndpoint.CORRECT,
            'fix': APIEndpoint.CORRECT,
            'grammar': APIEndpoint.CORRECT,
            'spell': APIEndpoint.CORRECT,
            'quiz': APIEndpoint.QUIZ_CREATE,
            'test': APIEndpoint.QUIZ_CREATE,
            'feedback': APIEndpoint.FEEDBACK,
            'rate': APIEndpoint.FEEDBACK,
            'topics': APIEndpoint.QUIZ_TOPICS,
            'stats': APIEndpoint.QUIZ_STATS,
            'magic': APIEndpoint.MAGIC,
        }
    
    async def route_request(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Intelligently route user request to appropriate API
        
        Args:
            user_input: User's input text
            context: Optional context (quiz_id, previous state, etc.)
        
        Returns:
            API response with routing information
        """
        # Detect intent
        endpoint = self._detect_endpoint(user_input, context)
        
        if not endpoint:
            return {
                'routed': False,
                'message': 'No specific API endpoint detected',
                'suggestion': 'Processing as general query'
            }
        
        # Route to appropriate endpoint
        try:
            result = await self._call_endpoint(endpoint, user_input, context)
            result['routed'] = True
            result['endpoint'] = endpoint.value
            return result
        except Exception as e:
            logger.error(f"API routing failed for {endpoint}: {e}")
            return {
                'routed': False,
                'error': str(e),
                'endpoint': endpoint.value
            }
    
    def _detect_endpoint(self, user_input: str, context: Optional[Dict] = None) -> Optional[APIEndpoint]:
        """
        Detect which API endpoint to use
        
        Args:
            user_input: User's input
            context: Optional context
        
        Returns:
            Detected endpoint or None
        """
        user_input_lower = user_input.lower()
        
        # Check for explicit commands first
        if user_input_lower.startswith('/correct'):
            return APIEndpoint.CORRECT
        elif user_input_lower.startswith('/quiz'):
            if 'topics' in user_input_lower:
                return APIEndpoint.QUIZ_TOPICS
            elif 'stats' in user_input_lower:
                return APIEndpoint.QUIZ_STATS
            else:
                return APIEndpoint.QUIZ_CREATE
        elif user_input_lower.startswith('/feedback'):
            return APIEndpoint.FEEDBACK
        elif user_input_lower.startswith('/stats'):
            return APIEndpoint.FEEDBACK_STATS
        
        # Check context for quiz answer
        if context and context.get('active_quiz_id'):
            # If there's an active quiz and input is a number, it's likely an answer
            if user_input.strip().isdigit():
                return APIEndpoint.QUIZ_ANSWER
        
        # Check keyword triggers
        for keyword, endpoint in self.keyword_triggers.items():
            if keyword in user_input_lower:
                # Verify with pattern matching
                if self._matches_pattern(user_input_lower, endpoint):
                    return endpoint
        
        # Pattern matching for more complex detection
        for endpoint, patterns in self.intent_patterns.items():
            if self._matches_pattern(user_input_lower, endpoint):
                return endpoint
        
        return None
    
    def _matches_pattern(self, text: str, endpoint: APIEndpoint) -> bool:
        """Check if text matches any pattern for the endpoint"""
        patterns = self.intent_patterns.get(endpoint, [])
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    async def _call_endpoint(self, endpoint: APIEndpoint, user_input: str, 
                            context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Call the appropriate API endpoint
        
        Args:
            endpoint: Detected endpoint
            user_input: User input
            context: Optional context
        
        Returns:
            API response
        """
        context = context or {}
        
        # Route to appropriate handler
        if endpoint == APIEndpoint.CORRECT:
            return await self._call_correct(user_input)
        
        elif endpoint == APIEndpoint.MAGIC:
            return await self._call_magic(user_input)
        
        elif endpoint == APIEndpoint.QUIZ_CREATE:
            return await self._call_quiz_create(user_input)
        
        elif endpoint == APIEndpoint.QUIZ_ANSWER:
            return await self._call_quiz_answer(user_input, context)
        
        elif endpoint == APIEndpoint.QUIZ_RESULTS:
            return await self._call_quiz_results(context)
        
        elif endpoint == APIEndpoint.QUIZ_TOPICS:
            return await self._call_quiz_topics()
        
        elif endpoint == APIEndpoint.QUIZ_STATS:
            return await self._call_quiz_stats()
        
        elif endpoint == APIEndpoint.FEEDBACK:
            return await self._call_feedback(user_input, context)
        
        elif endpoint == APIEndpoint.FEEDBACK_STATS:
            return await self._call_feedback_stats()
        
        elif endpoint == APIEndpoint.FEEDBACK_REPORT:
            return await self._call_feedback_report()
        
        else:
            return {'error': f'Unknown endpoint: {endpoint}'}
    
    async def _call_correct(self, text: str) -> Dict[str, Any]:
        """Call grammar correction API"""
        # Extract text to correct
        if text.lower().startswith('/correct'):
            text = text[8:].strip()
        
        url = f"{self.base_url}/api/v1/correct"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'text': text}) as response:
                result = await response.json()
                return {
                    'type': 'correction',
                    'data': result,
                    'formatted': result.get('formatted_message', result.get('corrected', text))
                }
    
    async def _call_magic(self, text: str) -> Dict[str, Any]:
        """Call magical response API"""
        url = f"{self.base_url}/api/v1/magic"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'text': text}) as response:
                result = await response.json()
                return {
                    'type': 'magic',
                    'data': result,
                    'formatted': result.get('response', text)
                }
    
    async def _call_quiz_create(self, text: str) -> Dict[str, Any]:
        """Call quiz creation API"""
        # Parse quiz parameters
        parts = text.lower().replace('/quiz', '').strip().split()
        topic = parts[0] if parts else 'python'
        num_questions = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
        difficulty = parts[2] if len(parts) > 2 else None
        
        url = f"{self.base_url}/api/v1/quiz/create"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                'topic': topic,
                'num_questions': num_questions,
                'difficulty': difficulty
            }) as response:
                result = await response.json()
                return {
                    'type': 'quiz_create',
                    'data': result,
                    'quiz_id': result.get('quiz_id'),
                    'formatted': result.get('current_question', {}).get('formatted', 'Quiz created!')
                }
    
    async def _call_quiz_answer(self, text: str, context: Dict) -> Dict[str, Any]:
        """Call quiz answer submission API"""
        quiz_id = context.get('active_quiz_id')
        answer = int(text.strip()) - 1  # Convert to 0-based index
        
        url = f"{self.base_url}/api/v1/quiz/answer"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                'quiz_id': quiz_id,
                'answer': answer
            }) as response:
                result = await response.json()
                return {
                    'type': 'quiz_answer',
                    'data': result,
                    'correct': result.get('correct'),
                    'completed': result.get('completed'),
                    'formatted': result.get('message', 'Answer submitted!')
                }
    
    async def _call_quiz_results(self, context: Dict) -> Dict[str, Any]:
        """Call quiz results API"""
        quiz_id = context.get('quiz_id')
        
        url = f"{self.base_url}/api/v1/quiz/results/{quiz_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                return {
                    'type': 'quiz_results',
                    'data': result,
                    'formatted': result.get('celebration', 'Quiz complete!')
                }
    
    async def _call_quiz_topics(self) -> Dict[str, Any]:
        """Call quiz topics API"""
        url = f"{self.base_url}/api/v1/quiz/topics"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                topics = result.get('topics', [])
                formatted = self.personality.wrap_response(
                    f"Available quiz topics: {', '.join(topics)}",
                    'learning'
                )
                return {
                    'type': 'quiz_topics',
                    'data': result,
                    'topics': topics,
                    'formatted': formatted
                }
    
    async def _call_quiz_stats(self) -> Dict[str, Any]:
        """Call quiz statistics API"""
        url = f"{self.base_url}/api/v1/quiz/stats"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                return {
                    'type': 'quiz_stats',
                    'data': result,
                    'formatted': result.get('message', 'Stats retrieved!')
                }
    
    async def _call_feedback(self, text: str, context: Dict) -> Dict[str, Any]:
        """Call feedback submission API"""
        # Parse feedback
        feedback_type = 'neutral'
        if any(word in text.lower() for word in ['good', 'great', 'excellent', 'helpful', 'perfect']):
            feedback_type = 'positive'
        elif any(word in text.lower() for word in ['bad', 'poor', 'terrible', 'wrong', 'unhelpful']):
            feedback_type = 'negative'
        
        url = f"{self.base_url}/api/v1/feedback"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                'query': context.get('last_query', ''),
                'response': context.get('last_response', ''),
                'feedback_type': feedback_type,
                'comment': text
            }) as response:
                result = await response.json()
                formatted = self.personality.wrap_response(
                    "Thanks for your feedback! I'm always learning!",
                    'celebration'
                )
                return {
                    'type': 'feedback',
                    'data': result,
                    'formatted': formatted
                }
    
    async def _call_feedback_stats(self) -> Dict[str, Any]:
        """Call feedback statistics API"""
        url = f"{self.base_url}/api/v1/feedback/stats"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                return {
                    'type': 'feedback_stats',
                    'data': result,
                    'formatted': f"Satisfaction rate: {result.get('satisfaction_rate', 0)}%"
                }
    
    async def _call_feedback_report(self) -> Dict[str, Any]:
        """Call feedback report API"""
        url = f"{self.base_url}/api/v1/feedback/report"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                return {
                    'type': 'feedback_report',
                    'data': result,
                    'formatted': result.get('report', 'Report generated!')
                }
    
    def get_endpoint_suggestion(self, user_input: str) -> Optional[str]:
        """
        Get suggestion for which endpoint might be useful
        
        Args:
            user_input: User's input
        
        Returns:
            Suggestion string or None
        """
        endpoint = self._detect_endpoint(user_input, None)
        
        if not endpoint:
            return None
        
        suggestions = {
            APIEndpoint.CORRECT: "💡 Tip: I can check your grammar! Try: '/correct <your text>'",
            APIEndpoint.QUIZ_CREATE: "💡 Tip: Want to test your knowledge? Try: '/quiz <topic> <num>'",
            APIEndpoint.QUIZ_TOPICS: "💡 Tip: See available topics with: '/quiz topics'",
            APIEndpoint.FEEDBACK: "💡 Tip: Your feedback helps me improve! Use: '/feedback <comment>'",
        }
        
        return suggestions.get(endpoint)


# Singleton instance
_router_instance = None

def get_api_router(base_url: str = "http://localhost:8000") -> IntelligentAPIRouter:
    """Get or create API router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = IntelligentAPIRouter(base_url)
    return _router_instance
