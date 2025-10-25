"""
JARVIS Unified - Complete Integration of Original + Enhanced Features
Combines the full-featured original JARVIS with JARVIS 2.0 enhancements
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from core.logger import get_logger
from core.jarvis_brain import JarvisBrain
from core.intent_classifier_enhanced import EnhancedIntentClassifier
from core.prompt_engine_enhanced import EnhancedPromptEngine
from storage.contextual_memory_enhanced import EnhancedContextualMemory
from core.sentiment_analyzer import SentimentAnalyzer
from core.query_decomposer import QueryDecomposer
from core.semantic_matcher import SemanticMatcher

logger = get_logger(__name__)


class JarvisUnified:
    """
    Unified JARVIS combining:
    - Original: Web search, API routing, real-time data, transformers, LangChain
    - Enhanced: Intent classification, sentiment analysis, contextual memory, semantic matching
    """
    
    def __init__(self):
        logger.info("Initializing JARVIS Unified - Complete System")
        
        # Original JARVIS Brain (full features)
        self.brain = JarvisBrain()
        
        # Enhanced Components
        self.enhanced_classifier = EnhancedIntentClassifier()
        self.enhanced_prompt_engine = EnhancedPromptEngine()
        self.enhanced_memory = EnhancedContextualMemory()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.query_decomposer = QueryDecomposer()
        self.semantic_matcher = SemanticMatcher()
        
        # Session management
        self.session_id = None
        
        logger.info("JARVIS Unified initialized with all features")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process query using unified system.
        
        Args:
            query: User query
            context: Optional context
        
        Returns:
            Complete response
        """
        try:
            # 1. Enhanced Intent Classification
            enhanced_intent = await self.enhanced_classifier.classify(query, context)
            logger.info(f"Enhanced intent: {enhanced_intent.category.value} (confidence: {enhanced_intent.confidence:.2f})")
            
            # 2. Sentiment Analysis
            sentiment = self.sentiment_analyzer.analyze(query)
            logger.info(f"Sentiment: {sentiment['mood']} (intensity: {sentiment['intensity']:.1f})")
            
            # 3. Get Enhanced Context
            enhanced_context = await self.enhanced_memory.get_context_for_query(query)
            
            # 4. Merge contexts
            full_context = {
                **(context or {}),
                'enhanced_intent': enhanced_intent,
                'sentiment': sentiment,
                'enhanced_memory': enhanced_context,
                'intent': enhanced_intent  # For compatibility with original brain
            }
            
            # 5. Check if query needs decomposition
            if enhanced_intent.confidence < 0.6 or len(query.split()) > 15:
                tasks = await self.query_decomposer.decompose(query)
                if len(tasks) > 1:
                    logger.info(f"Query decomposed into {len(tasks)} tasks")
                    full_context['decomposed_tasks'] = tasks
            
            # 6. Use original JARVIS Brain for full response generation
            # (includes web search, API routing, transformers, etc.)
            response = await self.brain.generate_response(query, full_context)
            
            # 7. Adjust response based on sentiment
            if sentiment['mood'] == 'frustrated':
                response = self._add_supportive_tone(response)
            elif sentiment['mood'] == 'excited':
                response = self._add_enthusiastic_tone(response)
            
            # 8. Update enhanced memory
            await self.enhanced_memory.add_interaction(
                query,
                response,
                {
                    'intent': enhanced_intent.category.value,
                    'sentiment': sentiment['mood'],
                    'confidence': enhanced_intent.confidence
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Unified processing failed: {e}")
            # Fallback to original brain
            return await self.brain.generate_response(query, context)
    
    def _add_supportive_tone(self, response: str) -> str:
        """Add supportive tone for frustrated users."""
        supportive_prefixes = [
            "I understand this can be challenging. ",
            "Let me help break this down for you. ",
            "I'm here to help you through this. "
        ]
        
        if not any(response.startswith(prefix) for prefix in supportive_prefixes):
            import random
            return random.choice(supportive_prefixes) + response
        return response
    
    def _add_enthusiastic_tone(self, response: str) -> str:
        """Add enthusiastic tone for excited users."""
        if not response.endswith('!') and not response.endswith('✨'):
            return response + " ✨"
        return response
    
    async def start_session(self, session_id: str):
        """Start a new session."""
        self.session_id = session_id
        self.enhanced_memory.start_session(session_id)
        logger.info(f"Session started: {session_id}")
    
    async def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        enhanced_summary = await self.enhanced_memory.get_learning_summary()
        brain_status = self.brain.get_status()
        
        return {
            'session_id': self.session_id,
            'enhanced_features': enhanced_summary,
            'brain_status': brain_status,
            'total_interactions': enhanced_summary.get('total_interactions', 0)
        }
    
    async def get_greeting(self) -> str:
        """Get personalized greeting."""
        return await self.brain.generate_greeting()
    
    async def get_farewell(self) -> str:
        """Get personalized farewell."""
        return await self.brain.generate_farewell()
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        return {
            'unified_system': 'operational',
            'original_features': self.brain.get_status(),
            'enhanced_features': {
                'intent_classifier': self.enhanced_classifier.get_model_info(),
                'sentiment_analyzer': 'operational',
                'contextual_memory': 'operational',
                'semantic_matcher': 'operational',
                'query_decomposer': 'operational'
            },
            'session_id': self.session_id
        }


# Singleton instance
_jarvis_unified_instance = None


async def get_jarvis_unified() -> JarvisUnified:
    """Get or create unified JARVIS instance."""
    global _jarvis_unified_instance
    if _jarvis_unified_instance is None:
        _jarvis_unified_instance = JarvisUnified()
    return _jarvis_unified_instance
