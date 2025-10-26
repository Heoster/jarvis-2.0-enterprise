"""Main assistant orchestrator integrating all components."""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from core.models import UserInput, Response, Conversation
from core.nlp import NLPEngine
from core.decision_engine import DecisionEngine
from core.action_planner import ActionPlanner
from core.action_executor import DefaultActionExecutor
from core.retrieval import RetrievalSystem
from core.ai_client import AIClient
from core.realtime_data import RealTimeDataManager
from core.vision import VisionEngine
from core.prompt_engine import PromptEngine
from core.response_generator import ResponseGenerator
from core.config import Config, get_config
from storage.memory_store import MemoryStore
from storage.vector_db import VectorDB
from storage.knowledge_cache import KnowledgeCache
from storage.contextual_memory import ContextualMemory
from monitoring.consent_manager import ConsentManager
from core.logger import get_logger, setup_logging
import uuid

logger = get_logger(__name__)


class Assistant:
    """Main assistant orchestrator."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize assistant with all components.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        
        # Setup logging
        setup_logging(
            log_level=self.config.logging.level,
            log_file=self.config.logging.file,
            max_size_mb=self.config.logging.max_size_mb,
            retention_days=self.config.logging.retention_days,
            use_json=(self.config.logging.format == "json"),
            redact_sensitive=self.config.logging.redact_sensitive
        )
        
        # Initialize components
        self._init_components()
        
        # Track startup time
        self.start_time = datetime.utcnow()
        
        logger.info("Assistant initialized successfully")
    
    def _init_components(self) -> None:
        """Initialize all assistant components."""
        # Storage layer
        self.memory_store = MemoryStore(
            db_path=self.config.database.memory_db,
            enable_wal=self.config.database.enable_wal
        )
        
        self.vector_db = VectorDB(
            index_path=self.config.database.vector_index
        )
        
        self.knowledge_cache = KnowledgeCache(
            db_path=self.config.database.cache_db,
            enable_wal=self.config.database.enable_wal
        )
        
        # Contextual memory with learning
        self.contextual_memory = ContextualMemory(
            memory_store=self.memory_store,
            max_turns=3  # Keep last 3 conversation turns
        )
        
        # NLP and understanding
        self.nlp_engine = NLPEngine(
            model_name=self.config.models.nlp.spacy_model
        )
        
        self.decision_engine = DecisionEngine()
        
        # Planning and execution
        self.action_planner = ActionPlanner()
        self.action_executor = DefaultActionExecutor()
        
        # Retrieval
        self.retrieval_system = RetrievalSystem(
            memory_store=self.memory_store,
            knowledge_cache=self.knowledge_cache,
            use_reranking=self.config.retrieval.use_reranking
        )
        
        # AI and generation
        self.ai_client = AIClient(
            use_dialogflow=self.config.models.ai.use_dialogflow,
            dialogflow_project_id=self.config.models.ai.dialogflow_project_id,
            local_model=self.config.models.ai.local_model
        )
        
        # Real-time data
        self.realtime_data = RealTimeDataManager(
            weather_api_key=self.config.apis.weather.api_key,
            news_api_key=self.config.apis.news.api_key
        )
        
        # Computer vision
        if self.config.models.vision.enabled:
            self.vision_engine = VisionEngine()
        else:
            self.vision_engine = None
        
        self.prompt_engine = PromptEngine(
            personality=self.config.assistant.personality
        )
        
        self.response_generator = ResponseGenerator(
            personality=self.config.assistant.personality
        )
        
        # Security and monitoring
        self.consent_manager = ConsentManager()
        
        logger.info("All components initialized")
    
    async def process_query(
        self,
        text: str,
        source: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Process user query through complete pipeline.
        
        Args:
            text: User input text
            source: Input source (text, voice, api)
            metadata: Additional metadata
            
        Returns:
            Response object
        """
        start_time = time.time()
        
        try:
            # Create user input
            user_input = UserInput(
                text=text,
                source=source,
                metadata=metadata or {}
            )
            
            logger.info(f"Processing query: {text[:50]}...")
            
            # Step 1: NLP Analysis
            nlp_result = await self.nlp_engine.analyze(text)
            
            # Step 2: Get contextual memory
            memory_context = await self.contextual_memory.get_context_for_query(text)
            
            # Step 3: Intent Classification (with context)
            intent = await self.decision_engine.classify_intent(user_input)
            
            # Check if clarification needed
            if self.decision_engine.should_clarify(intent):
                return await self._generate_clarification_response(intent)
            
            # Step 4: Retrieve Context
            context_docs = await self.retrieval_system.retrieve(
                query=text,
                top_k=self.config.retrieval.top_k_dense
            )
            
            # Step 5: Fetch real-time data if needed
            realtime_context = await self._fetch_realtime_data(text, intent)
            
            # Step 6: Create Action Plan with memory context
            context = {
                'query': text,
                'nlp_result': nlp_result,
                'context_docs': context_docs,
                'realtime_data': realtime_context,
                'memory_context': memory_context,
                'user_preferences': memory_context.get('user_preferences', {})
            }
            action_plan = await self.action_planner.plan(intent, context)
            
            # Step 7: Execute Actions
            execution_results = await self.action_executor.execute_plan(action_plan)
            
            # Step 8: Apply user preferences to response generation
            response_preferences = await self._get_response_preferences()
            
            # Step 9: Generate Response using AI with memory context
            response_context = {
                'text': text,
                'execution_results': execution_results,
                'confidence': intent.confidence,
                'realtime_data': realtime_context,
                'memory_context': memory_context,
                'preferences': response_preferences
            }
            
            # Use Jarvis for response generation with contextual memory
            jarvis_context = {
                'session_id': metadata.get('session_id', 'default') if metadata else 'default',
                'realtime_data': realtime_context,
                'execution_results': execution_results,
                'confidence': intent.confidence,
                'intent': intent,
                'conversation_history': self.contextual_memory.get_formatted_context(),
                'user_preferences': response_preferences
            }
            
            ai_response = await self.ai_client.generate(
                prompt=text,  # Jarvis handles context internally
                context=jarvis_context
            )
            
            response_data = await self.response_generator.generate(
                intent=intent,
                context=response_context,
                sources=context_docs,
                ai_response=ai_response
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create response object
            response = Response(
                text=response_data['text'],
                sources=context_docs,
                confidence=response_data['confidence'],
                suggestions=response_data.get('suggestions', []),
                metadata=response_data.get('metadata', {}),
                execution_time=execution_time
            )
            
            # Store conversation in both systems
            await self._store_conversation(user_input, response, intent, action_plan.actions)
            
            # Add to contextual memory for learning
            await self.contextual_memory.add_interaction(
                user_input=text,
                assistant_response=response.text,
                metadata={
                    'intent': intent.category.value,
                    'confidence': intent.confidence,
                    'execution_time': execution_time
                }
            )
            
            logger.info(f"Query processed in {execution_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return await self._generate_error_response(str(e))
    
    async def _generate_clarification_response(self, intent) -> Response:
        """Generate clarification request."""
        clarification = self.response_generator.generate_clarification_request(
            options=["option 1", "option 2"]
        )
        
        return Response(
            text=clarification['text'],
            sources=[],
            confidence=0.0,
            suggestions=clarification['suggestions'],
            metadata=clarification['metadata'],
            execution_time=0.0
        )
    
    async def _generate_error_response(self, error_message: str) -> Response:
        """Generate error response."""
        error_response = self.response_generator.generate_error_response(
            error_message=error_message,
            suggestion="Please try rephrasing your request."
        )
        
        return Response(
            text=error_response['text'],
            sources=[],
            confidence=0.0,
            suggestions=error_response['suggestions'],
            metadata=error_response['metadata'],
            execution_time=0.0
        )
    
    async def _fetch_realtime_data(self, text: str, intent) -> Dict[str, Any]:
        """
        Fetch real-time data based on query.
        
        Args:
            text: User query
            intent: Classified intent
            
        Returns:
            Real-time data context
        """
        realtime_context = {}
        text_lower = text.lower()
        
        try:
            # Weather queries
            if any(word in text_lower for word in ['weather', 'temperature', 'forecast']):
                # Extract location (simple approach)
                location = "India"  # Default, should be extracted from NLP
                weather_data = await self.realtime_data.get_weather(location)
                realtime_context['weather'] = weather_data
            
            # News queries
            if any(word in text_lower for word in ['news', 'headlines', 'latest']):
                news_data = await self.realtime_data.get_news(limit=5)
                realtime_context['news'] = news_data
            
            # Search queries
            if any(word in text_lower for word in ['search', 'find', 'look up']):
                search_results = await self.realtime_data.search_web(text, limit=5)
                realtime_context['search'] = search_results
            
            # Knowledge queries
            if any(word in text_lower for word in ['what is', 'who is', 'tell me about']):
                # Extract topic (simple approach)
                words = text.split()
                if 'about' in words:
                    topic_idx = words.index('about') + 1
                    if topic_idx < len(words):
                        topic = ' '.join(words[topic_idx:])
                        knowledge_data = await self.realtime_data.get_knowledge(topic)
                        realtime_context['knowledge'] = knowledge_data
        
        except Exception as e:
            logger.error(f"Failed to fetch real-time data: {e}")
        
        return realtime_context
    
    def _build_prompt(self, text: str, context: Dict[str, Any], sources: List) -> str:
        """
        Build prompt for AI generation.
        
        Args:
            text: User query
            context: Response context
            sources: Retrieved sources
            
        Returns:
            Formatted prompt
        """
        prompt_parts = [f"User query: {text}"]
        
        if context.get('realtime_data'):
            prompt_parts.append("\nReal-time information:")
            for key, value in context['realtime_data'].items():
                prompt_parts.append(f"- {key}: {value}")
        
        if sources:
            prompt_parts.append("\nRelevant context:")
            for source in sources[:3]:
                prompt_parts.append(f"- {source.get('text', '')[:200]}")
        
        prompt_parts.append("\nProvide a helpful, accurate response:")
        
        return "\n".join(prompt_parts)
    
    async def _get_response_preferences(self) -> Dict[str, Any]:
        """Get user preferences for response generation"""
        prefs = await self.contextual_memory.user_preferences.get_all_preferences()
        
        # Convert learned patterns to response preferences
        response_prefs = {
            'use_examples': False,
            'detailed': False,
            'concise': False,
            'step_by_step': False
        }
        
        if 'explanation_style' in prefs:
            style_prefs = prefs['explanation_style']
            
            # If user has asked for examples multiple times, always include them
            if style_prefs.get('use_examples', 0) > 2:
                response_prefs['use_examples'] = True
            
            if style_prefs.get('always_use_examples'):
                response_prefs['use_examples'] = True
            
            # Determine preferred detail level
            if style_prefs.get('detailed', 0) > style_prefs.get('concise', 0):
                response_prefs['detailed'] = True
            elif style_prefs.get('concise', 0) > 2:
                response_prefs['concise'] = True
            
            if style_prefs.get('step_by_step', 0) > 2:
                response_prefs['step_by_step'] = True
        
        return response_prefs
    
    async def _store_conversation(self, user_input, response, intent, actions) -> None:
        """Store conversation in memory."""
        try:
            conversation = Conversation(
                id=str(uuid.uuid4()),
                user_input=user_input.text,
                assistant_response=response.text,
                intent=intent,
                actions=actions
            )
            
            await self.memory_store.store_conversation(conversation)
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
    
    async def get_conversation_history(self, limit: int = 10) -> list:
        """
        Get recent conversation history.
        
        Args:
            limit: Number of conversations to retrieve
            
        Returns:
            List of conversations
        """
        return await self.memory_store.get_conversation_history(limit=limit)
    
    async def provide_feedback(self, feedback: str, context: Optional[Dict] = None):
        """
        Provide feedback to help Jarvis learn.
        
        Args:
            feedback: User feedback
            context: Context of the interaction
        """
        await self.contextual_memory.learn_from_feedback(feedback, context or {})
        logger.info(f"Feedback received: {feedback[:50]}...")
    
    async def set_preference(self, category: str, preference: str, value: Any):
        """
        Manually set a user preference.
        
        Args:
            category: Preference category
            preference: Specific preference
            value: Preference value
        """
        await self.contextual_memory.user_preferences.learn_preference(
            category=category,
            preference=preference,
            value=value,
            confidence=1.0
        )
        logger.info(f"Preference set: {category}.{preference} = {value}")
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of what Jarvis has learned about the user.
        
        Returns:
            Learning summary dictionary
        """
        return await self.contextual_memory.get_learning_summary()
    
    def start_session(self, session_id: str, metadata: Optional[Dict] = None):
        """
        Start a new conversation session.
        
        Args:
            session_id: Unique session identifier
            metadata: Session metadata
        """
        self.contextual_memory.start_session(session_id, metadata)
        logger.info(f"Started session: {session_id}")
    
    def clear_session(self):
        """Clear current conversation session"""
        self.contextual_memory.clear_session()
        logger.info("Session cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get assistant status.
        
        Returns:
            Status dictionary
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'status': 'running',
            'uptime_seconds': uptime,
            'config': {
                'personality': self.config.assistant.personality,
                'language': self.config.assistant.language
            },
            'components': {
                'nlp': 'ready',
                'ai': 'ready',
                'ai_backends': self.ai_client.get_available_backends(),
                'retrieval': 'ready',
                'memory': 'ready',
                'realtime_data': 'ready',
                'vision': 'ready' if self.vision_engine else 'disabled'
            }
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown assistant."""
        logger.info("Shutting down assistant...")
        
        # Save state
        self.vector_db.save()
        
        # Close connections
        self.memory_store.close()
        self.knowledge_cache.close()
        self.vector_db.close()
        
        logger.info("Assistant shutdown complete")
