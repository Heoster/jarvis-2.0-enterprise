"""Unified JARVIS with all enhanced features integrated."""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.logger import get_logger
from core.models import Intent, IntentCategory

logger = get_logger(__name__)


class UnifiedJarvis:
    """
    Unified JARVIS combining all enhanced features:
    - Enhanced intent classification with NER
    - Semantic matching
    - Contextual memory with student profiles
    - Query decomposition
    - Sentiment analysis
    - Knowledge graph tracking
    - Magical prompt engineering
    """
    
    def __init__(
        self,
        student_id: str = "heoster",
        personality: str = "magical_mentor",
        enable_all_features: bool = True
    ):
        self.student_id = student_id
        self.personality = personality
        self.enable_all_features = enable_all_features
        
        # Initialize enhanced components
        self._initialize_components()
        
        logger.info(f"Unified JARVIS initialized for {student_id}")
    
    def _initialize_components(self):
        """Initialize all enhanced components."""
        try:
            # Enhanced Intent Classification
            from core.intent_classifier_enhanced import EnhancedIntentClassifier
            self.enhanced_classifier = EnhancedIntentClassifier()
            logger.info("✅ Enhanced intent classifier loaded")
        except Exception as e:
            logger.warning(f"Enhanced classifier unavailable: {e}")
            self.enhanced_classifier = None
        
        try:
            # Semantic Matching
            from core.semantic_matcher import SemanticMatcher
            self.semantic_matcher = SemanticMatcher()
            logger.info("✅ Semantic matcher loaded")
        except Exception as e:
            logger.warning(f"Semantic matcher unavailable: {e}")
            self.semantic_matcher = None
        
        try:
            # Enhanced Memory
            from storage.contextual_memory_enhanced import EnhancedContextualMemory
            self.enhanced_memory = EnhancedContextualMemory(student_id=self.student_id)
            logger.info("✅ Enhanced memory loaded")
        except Exception as e:
            logger.warning(f"Enhanced memory unavailable: {e}")
            self.enhanced_memory = None
        
        try:
            # Query Decomposer
            from core.query_decomposer import QueryDecomposer
            self.query_decomposer = QueryDecomposer()
            logger.info("✅ Query decomposer loaded")
        except Exception as e:
            logger.warning(f"Query decomposer unavailable: {e}")
            self.query_decomposer = None
        
        try:
            # Sentiment Analyzer
            from core.sentiment_analyzer import SentimentAnalyzer
            self.sentiment_analyzer = SentimentAnalyzer()
            logger.info("✅ Sentiment analyzer loaded")
        except Exception as e:
            logger.warning(f"Sentiment analyzer unavailable: {e}")
            self.sentiment_analyzer = None
        
        try:
            # Knowledge Graph
            from core.knowledge_graph import KnowledgeGraph
            self.knowledge_graph = KnowledgeGraph(student_id=self.student_id)
            logger.info("✅ Knowledge graph loaded")
        except Exception as e:
            logger.warning(f"Knowledge graph unavailable: {e}")
            self.knowledge_graph = None
        
        try:
            # Enhanced Prompt Engine
            from core.prompt_engine_enhanced import EnhancedPromptEngine
            self.prompt_engine = EnhancedPromptEngine(personality=self.personality)
            logger.info("✅ Enhanced prompt engine loaded")
        except Exception as e:
            logger.warning(f"Prompt engine unavailable: {e}")
            self.prompt_engine = None
        
        # Fallback to original JARVIS brain if needed
        try:
            from core.jarvis_brain import JarvisBrain
            self.jarvis_brain = JarvisBrain()
            logger.info("✅ Original JARVIS brain loaded as fallback")
        except Exception as e:
            logger.warning(f"Original JARVIS brain unavailable: {e}")
            self.jarvis_brain = None
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process query with all enhanced features.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Generated response
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # 1. Analyze sentiment
            sentiment = None
            if self.sentiment_analyzer:
                sentiment = self.sentiment_analyzer.analyze(query)
                logger.info(f"Sentiment: {sentiment['mood']} (confidence: {sentiment['confidence']:.2f})")
            
            # 2. Check if query needs decomposition
            if self.query_decomposer and self.query_decomposer._needs_decomposition(query):
                logger.info("Query requires decomposition")
                return await self._process_compound_query(query, sentiment, context)
            
            # 3. Process single query
            return await self._process_single_query(query, sentiment, context)
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return self._generate_error_response(str(e))
    
    async def _process_compound_query(
        self,
        query: str,
        sentiment: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Process compound query with decomposition."""
        tasks = await self.query_decomposer.decompose(query)
        logger.info(f"Decomposed into {len(tasks)} tasks")
        
        responses = []
        for i, task in enumerate(tasks, 1):
            logger.info(f"Processing task {i}/{len(tasks)}: {task['task']}")
            
            # Check dependencies
            deps = task.get('dependencies', [])
            if deps and not all(d < i-1 for d in deps):
                logger.warning(f"Dependencies not met for task {i}")
                continue
            
            # Process task
            response = await self._process_single_query(
                task['task'],
                sentiment,
                context
            )
            responses.append(f"**Step {i}:** {response}")
        
        return "\n\n".join(responses)
    
    async def _process_single_query(
        self,
        query: str,
        sentiment: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Process single query with all enhancements."""
        # 1. Enhanced intent classification
        intent = None
        if self.enhanced_classifier:
            intent = await self.enhanced_classifier.classify(query, context)
            logger.info(f"Intent: {intent.category.value} (confidence: {intent.confidence:.2f})")
        
        # 2. Get adaptive context from memory
        adaptive_context = {}
        if self.enhanced_memory:
            adaptive_context = self.enhanced_memory.get_adaptive_context()
            logger.debug(f"Adaptive context: {adaptive_context.get('emotional_state')}")
        
        # 3. Build enhanced prompt
        prompt = query
        if self.prompt_engine and intent:
            prompt = self.prompt_engine.build_prompt(
                intent=intent,
                query=query,
                student_name=self.student_id.title(),
                emotional_state=sentiment['mood'] if sentiment else 'neutral',
                **adaptive_context
            )
        
        # 4. Generate response (use original JARVIS brain or simple response)
        if self.jarvis_brain:
            response = await self.jarvis_brain.generate_response(query, context)
        else:
            response = self._generate_simple_response(query, intent, sentiment)
        
        # 5. Add magical touch based on sentiment
        if sentiment and self.prompt_engine:
            response = self.prompt_engine.add_magical_touch(
                response,
                sentiment=sentiment['mood']
            )
        
        # 6. Update memory
        if self.enhanced_memory:
            self.enhanced_memory.add_exchange(
                user_input=query,
                assistant_response=response,
                intent=intent.category.value if intent else None,
                sentiment=sentiment['mood'] if sentiment else 'neutral'
            )
        
        # 7. Track concept in knowledge graph
        if self.knowledge_graph and intent:
            self._track_concept(query, intent)
        
        return response
    
    def _generate_simple_response(
        self,
        query: str,
        intent: Optional[Intent],
        sentiment: Optional[Dict[str, Any]]
    ) -> str:
        """Generate simple response when JARVIS brain unavailable."""
        if not intent:
            return "I'm processing your request. How can I help you further?"
        
        category = intent.category
        
        if category == IntentCategory.QUESTION:
            return f"That's a great question about {query}. Let me help you understand this concept."
        elif category == IntentCategory.CODE:
            return "I can help you with that code. Let me provide a solution."
        elif category == IntentCategory.MATH:
            return "I'll calculate that for you."
        elif category == IntentCategory.COMMAND:
            return "I'll execute that command."
        else:
            return "I'm here to help! What would you like to know?"
    
    def _track_concept(self, query: str, intent: Intent):
        """Track concepts in knowledge graph."""
        # Extract potential concepts from query
        concepts = []
        
        query_lower = query.lower()
        
        # Common programming concepts
        concept_keywords = {
            'function': 'functions',
            'loop': 'loops',
            'class': 'classes',
            'variable': 'variables',
            'list': 'lists',
            'dictionary': 'dictionaries',
            'minecraft': 'minecraft_basics',
            'mod': 'forge_setup'
        }
        
        for keyword, concept in concept_keywords.items():
            if keyword in query_lower:
                concepts.append(concept)
        
        # Record attempts for identified concepts
        for concept in concepts:
            if concept in self.knowledge_graph.graph:
                self.knowledge_graph.record_attempt(concept, success=True)
                logger.debug(f"Tracked concept: {concept}")
    
    def _generate_error_response(self, error: str) -> str:
        """Generate friendly error response."""
        return f"🔧 Oops! I encountered an issue: {error}\n\nLet me try a different approach. Could you rephrase your question?"
    
    def get_student_progress(self) -> Dict[str, Any]:
        """Get comprehensive student progress report."""
        progress = {
            'student_id': self.student_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Memory stats
        if self.enhanced_memory:
            progress['memory'] = {
                'total_interactions': self.enhanced_memory.student_profile.get('total_interactions', 0),
                'session_count': self.enhanced_memory.student_profile.get('session_count', 0),
                'emotional_state': self.enhanced_memory.student_profile.get('emotional_state'),
                'learning_style': self.enhanced_memory.student_profile.get('learning_style')
            }
        
        # Knowledge graph stats
        if self.knowledge_graph:
            mastered = {
                node for node in self.knowledge_graph.graph.nodes()
                if self.knowledge_graph.graph.nodes[node].get('mastered', False)
            }
            progress['knowledge'] = self.knowledge_graph.get_progress_summary(mastered)
        
        return progress
    
    def get_learning_recommendations(self) -> List[str]:
        """Get personalized learning recommendations."""
        recommendations = []
        
        if self.knowledge_graph and self.enhanced_memory:
            # Get mastered concepts
            mastered = {
                node for node in self.knowledge_graph.graph.nodes()
                if self.knowledge_graph.graph.nodes[node].get('mastered', False)
            }
            
            # Get next concepts
            next_concepts = self.knowledge_graph.get_next_concepts(mastered, max_difficulty=5)
            
            for concept, score in next_concepts[:3]:
                info = self.knowledge_graph.get_concept_info(concept)
                recommendations.append(
                    f"📚 {concept.replace('_', ' ').title()} "
                    f"(Difficulty: {'⭐' * info['difficulty']}, Readiness: {score:.1f})"
                )
        
        return recommendations
    
    async def end_session(self):
        """End session and save all data."""
        logger.info("Ending session...")
        
        # Save memory
        if self.enhanced_memory:
            self.enhanced_memory.save_student_profile()
            logger.info("✅ Student profile saved")
        
        # Save knowledge graph
        if self.knowledge_graph:
            self.knowledge_graph.save_graph()
            logger.info("✅ Knowledge graph saved")
        
        # Generate session summary
        if self.enhanced_memory:
            summary = self.enhanced_memory.get_session_summary()
            logger.info(f"Session summary: {summary}")
            return summary
        
        return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            'student_id': self.student_id,
            'personality': self.personality,
            'components': {
                'enhanced_classifier': self.enhanced_classifier is not None,
                'semantic_matcher': self.semantic_matcher is not None,
                'enhanced_memory': self.enhanced_memory is not None,
                'query_decomposer': self.query_decomposer is not None,
                'sentiment_analyzer': self.sentiment_analyzer is not None,
                'knowledge_graph': self.knowledge_graph is not None,
                'prompt_engine': self.prompt_engine is not None,
                'jarvis_brain': self.jarvis_brain is not None
            },
            'features_enabled': self.enable_all_features
        }
