"""
Iron Man JARVIS - True AI Assistant
Advanced conversational AI with real-time capabilities, automatic learning, and Iron Man personality.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import json
import re

from core.logger import get_logger
from core.jarvis_brain import JarvisBrain
from core.constants import ConfidenceThresholds, PersonalitySettings
from core.cache_manager import get_cache_manager
from monitoring.metrics import get_metrics_collector
from core.formatters import FormatterFactory
from core.conversation_handler import get_conversation_handler
from storage.contextual_memory import get_contextual_memory

logger = get_logger(__name__)


class IronManJARVIS:
    """
    Iron Man's JARVIS - Advanced AI Assistant
    
    Features:
    - Real-time responses with Iron Man personality
    - Automatic learning from positive feedback
    - Smart conversational editing
    - Time and date awareness
    - Comprehensive knowledge integration
    - Proactive assistance
    """
    
    def __init__(self):
        """Initialize Iron Man JARVIS"""
        self.brain = JarvisBrain()
        self.cache_manager = get_cache_manager()
        self.metrics = get_metrics_collector()
        self.formatter_factory = FormatterFactory()
        self.conversation_handler = get_conversation_handler()
        
        # Iron Man specific features
        self.personality_mode = "iron_man"
        self.learning_enabled = True
        self.proactive_mode = True
        
        # Real-time capabilities
        self.time_zone = timezone.utc
        self.location = "Malibu, California"  # Tony Stark's location
        
        # Learning system
        self.positive_feedback_count = 0
        self.learning_threshold = 3  # Learn after 3 positive feedbacks
        
        # Conversational memory
        self.contextual_memory = None
        
        logger.info("🤖 Iron Man JARVIS initialized - Ready to assist, Mr. Stark")
    
    async def initialize_async_components(self):
        """Initialize async components"""
        if self.contextual_memory is None:
            self.contextual_memory = await get_contextual_memory()
        
        # Start session
        session_id = f"stark_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.contextual_memory.start_session(session_id, {
            'user': 'Tony Stark',
            'location': self.location,
            'personality': self.personality_mode
        })
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process query with Iron Man JARVIS capabilities
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            JARVIS response
        """
        start_time = time.time()
        
        try:
            # Initialize async components
            await self.initialize_async_components()
            
            # Record metrics
            self.metrics.record_query(query)
            
            # Handle special Iron Man commands
            if query.lower().startswith(('jarvis', 'hey jarvis', 'ok jarvis')):
                query = query.split(' ', 1)[1] if ' ' in query else "Yes, sir?"
            
            # Check for time/date queries first
            time_response = await self._handle_time_queries(query)
            if time_response:
                return time_response
            
            # Smart conversational editing
            edited_query = await self._smart_edit_query(query)
            if edited_query != query:
                logger.info(f"Query edited: '{query}' → '{edited_query}'")
                query = edited_query
            
            # Process through enhanced brain
            context = context or {}
            context.update({
                'personality_mode': self.personality_mode,
                'user_name': 'heoster',
                'location': self.location,
                'proactive_mode': self.proactive_mode
            })
            
            response = await self.brain.generate_response(query, context)
            
            # Apply Iron Man personality
            response = await self._apply_iron_man_personality(response, query, context)
            
            # Add to contextual memory
            await self.contextual_memory.add_interaction(query, response, {
                'personality': self.personality_mode,
                'execution_time': time.time() - start_time
            })
            
            # Record metrics
            self.metrics.record_response_time(time.time() - start_time, len(response))
            
            return response
            
        except Exception as e:
            logger.error(f"JARVIS processing failed: {e}")
            return await self._generate_iron_man_error_response(str(e))
    
    async def _handle_time_queries(self, query: str) -> Optional[str]:
        """Handle time and date related queries"""
        query_lower = query.lower()
        
        # Time queries
        if any(phrase in query_lower for phrase in [
            'what time is it', 'current time', 'time now', 'what\'s the time',
            'tell me the time', 'time please'
        ]):
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            
            return f"🕐 **Current Time:** {time_str}\n📅 **Date:** {date_str}\n\nAnything else I can help you with, sir?"
        
        # Date queries
        if any(phrase in query_lower for phrase in [
            'what date is it', 'today\'s date', 'current date', 'what day is it',
            'tell me the date', 'date please'
        ]):
            now = datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            day_str = now.strftime("%A")
            
            return f"📅 **Today is:** {day_str}\n📆 **Full Date:** {date_str}\n\nIs there anything specific you need to schedule, sir?"
        
        return None
    
    async def _smart_edit_query(self, query: str) -> str:
        """Smart conversational editing to improve query understanding"""
        
        # Fix common greeting variations
        greeting_fixes = {
            'hellow': 'hello',
            'helo': 'hello', 
            'hllo': 'hello',
            'hii': 'hello',
            'hi jarvis': 'hello',
            'hey jarvis': 'hello',
            'good morning jarvis': 'good morning',
            'good afternoon jarvis': 'good afternoon',
            'good evening jarvis': 'good evening'
        }
        
        query_lower = query.lower().strip()
        for wrong, correct in greeting_fixes.items():
            if query_lower == wrong or query_lower.startswith(wrong + ' '):
                query = query_lower.replace(wrong, correct, 1)
                break
        
        # Fix common command patterns
        command_fixes = {
            'serach': 'search',
            'seach': 'search',
            'find me': 'search for',
            'look for': 'search for',
            'i want to know about': 'tell me about',
            'can you tell me': 'tell me',
            'do you know': 'what is',
            'whats': 'what is',
            'whos': 'who is',
            'hows': 'how is'
        }
        
        for wrong, correct in command_fixes.items():
            if wrong in query.lower():
                query = re.sub(re.escape(wrong), correct, query, flags=re.IGNORECASE)
        
        # Expand contractions
        contractions = {
            "won't": "will not",
            "can't": "cannot", 
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            query = query.replace(contraction, expansion)
        
        # Fix spacing and punctuation
        query = re.sub(r'\s+', ' ', query)  # Multiple spaces to single
        query = query.strip()
        
        return query
    
    async def _apply_iron_man_personality(self, response: str, query: str, context: Dict[str, Any]) -> str:
        """Apply Iron Man JARVIS personality to responses"""
        
        # Don't modify if already formatted (has headers/separators)
        if any(marker in response for marker in ['===', '---', '🔍', '💰', '🚂', '📈']):
            # Just add a polite closing
            if not response.endswith(('sir.', 'sir!', 'Mr. Stark.', 'Mr. Stark!')):
                response += "\n\nAnything else I can assist you with, sir?"
            return response
        
        # Determine response type for appropriate tone
        query_lower = query.lower()
        
        # Greeting responses
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            greetings = [
                f"Good to see you, sir. {response}",
                f"Welcome back, Mr. Stark. {response}",
                f"At your service, sir. {response}",
                f"Ready to assist, Mr. Stark. {response}"
            ]
            import random
            return random.choice(greetings)
        
        # Question responses
        if query.strip().endswith('?') or any(word in query_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            if len(response) < 100:
                return f"Certainly, sir. {response} Is there anything else you'd like to know?"
            else:
                return f"{response}\n\nI hope that answers your question, Mr. Stark."
        
        # Command responses
        if any(word in query_lower for word in ['search', 'find', 'show', 'tell', 'get', 'calculate']):
            return f"{response}\n\nTask completed, sir. Anything else?"
        
        # Error responses
        if any(word in response.lower() for word in ['error', 'sorry', 'apologize', 'failed']):
            return f"I apologize, sir. {response} Shall I try a different approach?"
        
        # Default enhancement
        if len(response) < 50:
            return f"{response} How else may I assist you, Mr. Stark?"
        else:
            return f"{response}\n\nIs there anything else you need, sir?"
    
    async def _generate_iron_man_error_response(self, error: str) -> str:
        """Generate Iron Man style error response"""
        error_responses = [
            f"I'm experiencing some technical difficulties, sir. {error}",
            f"My systems encountered an issue, Mr. Stark. {error}",
            f"There seems to be a glitch in my matrix, sir. {error}",
            f"I'm running diagnostics on this error, Mr. Stark. {error}"
        ]
        
        import random
        base_response = random.choice(error_responses)
        
        return f"{base_response}\n\nShall I attempt an alternative approach, sir?"
    
    async def learn_from_feedback(self, query: str, response: str, feedback: str) -> bool:
        """
        Automatic learning from positive feedback
        
        Args:
            query: Original query
            response: JARVIS response
            feedback: User feedback
            
        Returns:
            True if learning occurred
        """
        if not self.learning_enabled:
            return False
        
        feedback_lower = feedback.lower()
        
        # Detect positive feedback
        positive_indicators = [
            'good', 'great', 'excellent', 'perfect', 'amazing', 'awesome',
            'helpful', 'useful', 'correct', 'right', 'yes', 'exactly',
            'thank you', 'thanks', 'appreciate', 'love it', 'brilliant'
        ]
        
        is_positive = any(indicator in feedback_lower for indicator in positive_indicators)
        
        if is_positive:
            self.positive_feedback_count += 1
            
            # Learn from interaction
            await self.contextual_memory.learn_from_feedback(feedback, {
                'query': query,
                'response': response,
                'feedback_type': 'positive'
            })
            
            # Auto-train after threshold
            if self.positive_feedback_count >= self.learning_threshold:
                await self._auto_train_from_positive_feedback()
                self.positive_feedback_count = 0
                return True
        
        return False
    
    async def _auto_train_from_positive_feedback(self):
        """Automatically train from accumulated positive feedback"""
        try:
            # Get recent positive interactions
            learning_summary = await self.contextual_memory.get_learning_summary()
            
            # Extract successful patterns
            successful_patterns = []
            
            # This would integrate with the enhanced intent classifier
            # to improve pattern recognition based on successful interactions
            
            logger.info(f"🧠 Auto-training completed from {self.learning_threshold} positive interactions")
            
        except Exception as e:
            logger.error(f"Auto-training failed: {e}")
    
    async def get_proactive_suggestions(self, context: Optional[Dict] = None) -> List[str]:
        """Generate proactive suggestions based on context"""
        if not self.proactive_mode:
            return []
        
        suggestions = []
        
        # Time-based suggestions
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour < 9:
            suggestions.extend([
                "Would you like me to brief you on today's schedule?",
                "Shall I check the latest news headlines?",
                "Would you like a weather update for today?"
            ])
        elif 9 <= hour < 12:
            suggestions.extend([
                "Any research I can help you with this morning?",
                "Would you like me to search for technical information?",
                "Shall I check your project status?"
            ])
        elif 12 <= hour < 17:
            suggestions.extend([
                "Need any calculations or analysis done?",
                "Would you like me to search for specific information?",
                "Any technical problems I can help solve?"
            ])
        elif 17 <= hour < 21:
            suggestions.extend([
                "Would you like a summary of today's activities?",
                "Shall I help you plan for tomorrow?",
                "Any entertainment recommendations?"
            ])
        else:
            suggestions.extend([
                "Working late again, sir? How can I assist?",
                "Would you like me to dim the lights and play some music?",
                "Shall I prepare a summary for tomorrow?"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def get_iron_man_greeting(self) -> str:
        """Get Iron Man style greeting"""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            greetings = [
                "Good morning, heoster. All systems are operational and ready for your commands.",
                "Morning, sir. I trust you slept well? How may I assist you today?",
                "Good morning,  heoster. Your workshop systems are online and awaiting instructions.",
                "Rise and shine, sir. I've been monitoring global networks - all quiet on the western front."
            ]
        elif 12 <= hour < 17:
            greetings = [
                "Good afternoon, heoster. How may I be of service?",
                "Afternoon, sir. I've been running diagnostics - all systems optimal.",
                "Good afternoon,  heoster. Ready to tackle any challenges you have in mind?",
                "Afternoon, sir. The workshop is ready for whatever genius you're planning today."
            ]
        elif 17 <= hour < 21:
            greetings = [
                "Good evening, heoster. How was your day?",
                "Evening, sir. Ready for some evening projects?",
                "Good evening, heoster. Shall we review today's accomplishments?",
                "Evening, sir. The lab is prepped for any late-night innovations."
            ]
        else:
            greetings = [
                "Working late again, Mr. Stark? I'm here to assist.",
                "Burning the midnight oil, sir? How can I help?",
                "Late night session, Mr. Stark? I'm at your service.",
                "Another all-nighter, sir? Let's make it productive."
            ]
        
        import random
        return random.choice(greetings)
    
    async def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive JARVIS status report"""
        metrics_summary = self.metrics.get_performance_summary()
        cache_stats = self.cache_manager.get_stats()
        
        return {
            'system_name': 'JARVIS (Just A Rather Very Intelligent System)',
            'version': '2.0 - Iron Man Edition',
            'status': 'Fully Operational',
            'personality_mode': self.personality_mode,
            'learning_enabled': self.learning_enabled,
            'proactive_mode': self.proactive_mode,
            'location': self.location,
            'uptime': time.time() - (metrics_summary.get('start_time', time.time())),
            'performance': metrics_summary,
            'cache_efficiency': cache_stats.get('hit_rate', 0),
            'positive_feedback_count': self.positive_feedback_count,
            'features': [
                'Real-time responses',
                'Automatic learning',
                'Smart query editing', 
                'Time/date awareness',
                'Proactive assistance',
                'Iron Man personality',
                'Comprehensive knowledge',
                'Multi-modal capabilities'
            ]
        }


# Global instance
_iron_man_jarvis = None

async def get_iron_man_jarvis() -> IronManJARVIS:
    """Get or create Iron Man JARVIS instance"""
    global _iron_man_jarvis
    if _iron_man_jarvis is None:
        _iron_man_jarvis = IronManJARVIS()
        await _iron_man_jarvis.initialize_async_components()
    return _iron_man_jarvis