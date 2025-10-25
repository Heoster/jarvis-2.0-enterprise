"""
Codeex Assistant - Enhanced Jarvis with Personality and Student Features
Integrates grammar correction, quizzes, knowledge expansion, and feedback
"""

from typing import Dict, Any, Optional
from datetime import datetime
from core.assistant import Assistant
from core.codeex_personality import CodeexPersonality
from core.grammar_corrector import get_corrector
from core.quiz_engine import get_quiz_engine
from core.knowledge_expander import get_knowledge_expander
from core.feedback_system import get_feedback_system
from core.logger import get_logger
from core.models import Response

logger = get_logger(__name__)


class CodeexAssistant(Assistant):
    """Enhanced assistant with Codeex personality and student features"""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize Codeex assistant"""
        super().__init__(config)
        
        # Initialize Codeex-specific components
        self.personality = CodeexPersonality()
        self.corrector = get_corrector()
        self.quiz_engine = get_quiz_engine()
        self.knowledge_expander = get_knowledge_expander()
        self.feedback_system = get_feedback_system()
        
        # Override system prompt with Codeex personality
        self.system_prompt = self.personality.create_system_prompt()
        
        logger.info("Codeex Assistant initialized with magical personality! ✨")
    
    async def process_query(
        self,
        text: str,
        source: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Process query with Codeex enhancements
        
        Args:
            text: User input
            source: Input source
            metadata: Additional metadata
        
        Returns:
            Enhanced response
        """
        # Detect special commands
        if text.lower().startswith('/correct '):
            return await self._handle_correction(text[9:])
        
        if text.lower().startswith('/quiz '):
            return await self._handle_quiz_command(text[6:])
        
        if text.lower().startswith('/help '):
            return await self._handle_help_request(text[6:])
        
        # Process normally with personality enhancement
        response = await super().process_query(text, source, metadata)
        
        # Enhance response with personality
        response.text = self.personality.wrap_response(
            response.text,
            self._determine_context(response)
        )
        
        return response
    
    async def _handle_correction(self, text: str) -> Response:
        """Handle grammar correction request"""
        result = self.corrector.correct_text(text)
        
        formatted = self.personality.format_correction(
            result['original'],
            result['corrected'],
            [c.get('message', str(c)) for c in result.get('corrections', [])]
        )
        
        return Response(
            text=formatted,
            intent='grammar_correction',
            confidence=1.0,
            sources=[{'type': 'grammar_corrector', 'data': result}]
        )
    
    async def _handle_quiz_command(self, command: str) -> Response:
        """Handle quiz commands"""
        parts = command.strip().split()
        
        if not parts:
            topics = self.quiz_engine.get_topics()
            message = self.personality.wrap_response(
                f"Available quiz topics: {', '.join(topics)}\n\nUse '/quiz <topic>' to start!",
                'learning'
            )
            return Response(text=message, intent='quiz_help', confidence=1.0)
        
        topic = parts[0]
        num_questions = int(parts[1]) if len(parts) > 1 else 5
        
        # Create quiz
        quiz = self.quiz_engine.generate_quiz(topic, num_questions)
        first_q = self.quiz_engine.get_current_question(quiz['id'])
        
        if first_q:
            formatted = self.personality.format_quiz_question(
                first_q['question'],
                first_q['options'],
                first_q.get('difficulty', 'medium')
            )
            
            formatted += f"\n\n💡 Quiz ID: {quiz['id']}\n"
            formatted += "Answer with: /answer <quiz_id> <option_number>"
            
            return Response(
                text=formatted,
                intent='quiz_start',
                confidence=1.0,
                sources=[{'type': 'quiz', 'quiz_id': quiz['id']}]
            )
        
        return Response(
            text=self.personality.get_fallback(),
            intent='quiz_error',
            confidence=0.5
        )
    
    async def _handle_help_request(self, query: str) -> Response:
        """Handle help requests with knowledge base"""
        # Search knowledge base
        results = self.knowledge_expander.search_knowledge(query)
        
        if not results:
            # Fall back to regular processing
            return await super().process_query(f"help with {query}")
        
        # Format top result
        top_result = results[0]
        
        if 'error' in top_result:
            # Modding error help
            formatted = self.personality.format_modding_help(
                'Minecraft',
                top_result.get('error', ''),
                top_result.get('solution', '')
            )
        else:
            # General help
            formatted = self.personality.format_code_help(
                query,
                top_result.get('content', ''),
                None
            )
        
        return Response(
            text=formatted,
            intent='help',
            confidence=0.9,
            sources=[{'type': 'knowledge_base', 'data': top_result}]
        )
    
    def _determine_context(self, response: Response) -> str:
        """Determine context for personality wrapper"""
        intent = response.intent.lower()
        
        if 'error' in intent or 'fail' in intent:
            return 'error'
        elif 'success' in intent or response.confidence > 0.8:
            return 'success'
        elif 'code' in intent or 'program' in intent:
            return 'coding'
        elif 'learn' in intent or 'study' in intent:
            return 'learning'
        else:
            return 'general'
    
    async def get_greeting(self) -> str:
        """Get personalized greeting"""
        return self.personality.get_greeting()
    
    async def record_feedback(self, query: str, response: str,
                             feedback_type: str, comment: Optional[str] = None):
        """Record user feedback"""
        self.feedback_system.record_feedback(
            query, response, feedback_type, comment
        )
        
        if feedback_type == 'positive':
            return self.personality.wrap_response(
                "Thanks for the feedback! I'm glad I could help!",
                'celebration'
            )
        elif feedback_type == 'negative':
            return self.personality.wrap_response(
                "Thanks for letting me know. I'll work on improving!",
                'learning'
            )
        else:
            return self.personality.wrap_response(
                "Thanks for your feedback!",
                'general'
            )
    
    async def get_stats(self) -> Dict:
        """Get comprehensive stats"""
        feedback_stats = self.feedback_system.get_feedback_stats()
        quiz_stats = self.quiz_engine.get_quiz_stats()
        
        return {
            'feedback': feedback_stats,
            'quizzes': quiz_stats,
            'knowledge_categories': self.knowledge_expander.get_category_list(),
            'uptime': (datetime.now() - self.start_time).total_seconds() if hasattr(self, 'start_time') else 0
        }
    
    async def generate_improvement_report(self) -> str:
        """Generate improvement report"""
        return self.feedback_system.generate_improvement_report()
    
    async def export_training_data(self, output_file: str):
        """Export feedback as training data"""
        count = self.feedback_system.export_training_data(output_file, 'positive')
        return self.personality.wrap_response(
            f"Exported {count} training examples to {output_file}!",
            'success'
        )


# Convenience function
def create_codeex_assistant(config: Optional[Any] = None) -> CodeexAssistant:
    """Create and return Codeex assistant instance"""
    return CodeexAssistant(config)
