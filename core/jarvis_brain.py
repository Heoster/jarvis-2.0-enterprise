"""
JARVIS Brain - Complete Iron Man AI Assistant
Advanced response generation with Iron Man personality, automatic learning, and comprehensive NLP
"""

import asyncio
import time
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from collections import deque

from core.logger import get_logger
from core.api_router import get_api_router, APIEndpoint
from core.heoster_personality import get_heoster_jarvis
from core.web_scraper import get_web_scraper
from core.indian_apis import get_indian_api
from core.conversation_handler import get_conversation_handler
from core.intent_router import get_intent_router
from core.intent_classifier_enhanced import EnhancedIntentClassifier
from core.constants import ConfidenceThresholds, ResponseLimits, PersonalitySettings
from core.formatters import FormatterFactory
from core.cache_manager import get_cache_manager
from monitoring.metrics import get_metrics_collector
from core.nlp import NLPEngine
from execution.math_engine import MathEngine
from core.vision import VisionEngine
from core.models import Intent, IntentCategory

logger = get_logger(__name__)


class JarvisBrain:
    """
    JARVIS Complete AI Brain - Iron Man Assistant
    
    Features:
    🤖 Iron Man Personality & Responses
    🧠 Advanced NLP with spaCy and Transformers
    ⏰ Real-time Time/Date Awareness
    💬 Smart Conversational Editing
    🎓 Automatic Learning from Feedback
    🔍 Advanced Web Search & Scraping
    💰 Real-time Financial Data (Bitcoin, Currency, Mutual Funds)
    🚂 Indian Railway Information
    🎭 Entertainment Content (Jokes, Quotes, Images)
    📚 Smart Knowledge Integration
    🎯 Proactive Assistance
    🔧 Enhanced Error Handling
    📊 Comprehensive Monitoring
    """
    
    def __init__(
        self,
        model_name: str = "facebook/blenderbot-400M-distill",
        temperature: float = 0.7,
        max_length: int = 200
    ):
        """
        Initialize Jarvis's brain.
        
        Args:
            model_name: Transformer model to use
            temperature: Response creativity (0.0-1.0)
            max_length: Maximum response length
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_length = max_length
        
        self.model = None
        self.tokenizer = None
        self.langchain_llm = None
        self.conversation_chain = None
        self.memory = []
        
        # Initialize intelligent API router
        self.api_router = get_api_router()
        
        # Initialize Heoster's personal Jarvis personality
        self.heoster_personality = get_heoster_jarvis()
        
        # Initialize intent router for centralized routing
        self.intent_router = get_intent_router()
        
        # Initialize enhanced intent classifier
        self.intent_classifier = EnhancedIntentClassifier()
        
        # Initialize formatter factory
        self.formatter_factory = FormatterFactory()
        
        # Initialize enhanced components
        self.cache_manager = get_cache_manager()
        self.metrics = get_metrics_collector()
        self.nlp_engine = NLPEngine()
        self.math_engine = MathEngine()
        self.vision_engine = VisionEngine()
        
        # Iron Man personality settings
        self.personality_mode = "iron_man"
        self.user_name = "heoster"
        self.location = "muzaffarnagar, India"
        
        # Learning and training
        self.learning_enabled = True
        self.positive_feedback_count = 0
        self.learning_threshold = 3
        self.training_data = deque(maxlen=100)
        
        # Conversational memory
        self.conversation_memory = deque(maxlen=10)
        self.context_awareness = True
        
        # Track active quiz state
        self.active_quiz_id = None
        self.last_query = None
        self.last_response = None
        
        # Web scraper will be initialized async
        self.web_scraper = None
        
        # Indian APIs will be initialized async
        self.indian_api = None
        
        # Conversation handler for natural language understanding
        self.conversation_handler = get_conversation_handler()
        
        self._initialize_components()
        
        logger.info("Enhanced Jarvis Brain initialized with new architecture")
        logger.info("✅ Intent Router: Centralized routing system")
        logger.info("✅ Enhanced Classifier: Multi-stage intent detection") 
        logger.info("✅ Formatter Factory: Standardized response formatting")
        logger.info("✅ Tool System: Modular capability framework")
        logger.info("Personal AI for Heoster, developed by Codeex AI Company")
        logger.info("Jarvis 2.0 is ready to assist with enhanced capabilities")
    
    def _initialize_components(self):
        """Initialize Transformers and LangChain components."""
        try:
            # Initialize Transformers
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            logger.info(f"Loading Jarvis's neural network: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            # Initialize LangChain
            self._initialize_langchain()
            
            logger.info("Jarvis is ready to assist")
            
        except ImportError as e:
            logger.warning(f"Some components not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Jarvis Brain: {e}")
    
    def _initialize_langchain(self):
        """Initialize LangChain components."""
        try:
            from langchain.llms.base import LLM
            from langchain.chains import ConversationChain
            from langchain.memory import ConversationBufferMemory
            from langchain.prompts import PromptTemplate
            from pydantic import Field
            from typing import Any, List, Optional
            
            # Create custom LLM wrapper for our transformer model
            class JarvisLLM(LLM):
                """Custom LangChain LLM wrapper for Jarvis."""
                
                model: Any = Field(default=None)
                tokenizer: Any = Field(default=None)
                max_length: int = Field(default=200)
                
                class Config:
                    arbitrary_types_allowed = True
                
                @property
                def _llm_type(self) -> str:
                    return "jarvis_transformer"
                
                def _call(
                    self,
                    prompt: str,
                    stop: Optional[List[str]] = None,
                    **kwargs: Any
                ) -> str:
                    """Generate response using transformer model."""
                    if not self.model or not self.tokenizer:
                        return "I apologize, but my neural network is not fully initialized."
                    
                    try:
                        inputs = self.tokenizer(
                            prompt,
                            return_tensors="pt",
                            max_length=512,
                            truncation=True
                        )
                        
                        outputs = self.model.generate(
                            **inputs,
                            max_length=self.max_length,
                            num_beams=5,
                            temperature=0.7,
                            do_sample=True,
                            top_p=0.9,
                            early_stopping=True
                        )
                        
                        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                        return response
                        
                    except Exception as e:
                        logger.error(f"Jarvis generation error: {e}")
                        return "I encountered a processing error. Please try again."
            
            # Initialize custom LLM
            self.langchain_llm = JarvisLLM(
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=self.max_length
            )
            
            # Create conversation memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create Jarvis-specific prompt template
            jarvis_template = """You are Jarvis, an advanced AI assistant inspired by Tony Stark's AI companion. You are:
- Intelligent, sophisticated, and highly capable
- Professional yet personable with a subtle wit
- Efficient and precise in your responses
- Knowledgeable across many domains
- Helpful and proactive

Current conversation:
{chat_history}
Human: {input}
Jarvis: """
            
            prompt = PromptTemplate(
                input_variables=["chat_history", "input"],
                template=jarvis_template
            )
            
            # Create conversation chain
            self.conversation_chain = ConversationChain(
                llm=self.langchain_llm,
                memory=memory,
                prompt=prompt,
                verbose=False
            )
            
            logger.info("LangChain conversation chain initialized for Jarvis")
            
        except ImportError:
            logger.warning("LangChain not available, using basic mode")
        except Exception as e:
            logger.error(f"LangChain initialization failed: {e}")
    
    async def generate_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate intelligent Iron Man JARVIS response with all enhanced features.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete JARVIS response with Iron Man personality
        """
        start_time = time.time()
        
        try:
            # Initialize async components
            await self._initialize_async_components()
            
            # Record metrics
            self.metrics.record_query(query)
            
            # Step 1: Smart Query Preprocessing
            processed_query = await self._smart_preprocess_query(query)
            
            # Step 2: Check for immediate responses (time, greetings, etc.)
            immediate_response = await self._check_immediate_responses(processed_query)
            if immediate_response:
                return await self._apply_iron_man_personality(immediate_response, processed_query)
            
            # Step 3: Enhanced NLP Analysis
            nlp_analysis = await self._enhanced_nlp_analysis(processed_query)
            
            # Step 4: Build comprehensive context
            enriched_context = await self._build_comprehensive_context(processed_query, context, nlp_analysis)
            
            # Step 5: Intent classification with enhanced features
            intent = await self._classify_intent_enhanced(processed_query, enriched_context)
            
            # Step 6: Route to appropriate handler
            response = await self._route_and_process(processed_query, intent, enriched_context)
            
            # Step 7: Apply Iron Man personality and enhancements
            final_response = await self._apply_iron_man_personality(response, processed_query)
            
            # Step 8: Update memory and learning
            await self._update_memory_and_learning(processed_query, final_response)
            
            # Step 9: Record metrics
            execution_time = time.time() - start_time
            self.metrics.record_response_time(execution_time, len(final_response))
            
            return final_response
            
        except Exception as e:
            logger.error(f"JARVIS response generation failed: {e}")
            return await self._generate_iron_man_error_response(str(e))
    
    async def _initialize_async_components(self):
        """Initialize async components if needed"""
        if self.web_scraper is None:
            self.web_scraper = await get_web_scraper()
        
        if self.indian_api is None:
            self.indian_api = await get_indian_api()
    
    async def _smart_preprocess_query(self, query: str) -> str:
        """
        Smart preprocessing with conversational editing and typo fixes
        """
        # Handle JARVIS wake words
        if query.lower().startswith(('jarvis', 'hey jarvis', 'ok jarvis')):
            query = query.split(' ', 1)[1] if ' ' in query else "Yes, sir?"
        
        # Fix common greeting variations
        greeting_fixes = {
            'hellow': 'hello',
            'helo': 'hello', 
            'hllo': 'hello',
            'helllo': 'hello',
            'hi jarvis': 'hello',
            'hey jarvis': 'hello'
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
            'whats': 'what is',
            'whos': 'who is',
            'hows': 'how is'
        }
        
        for wrong, correct in command_fixes.items():
            if wrong in query.lower():
                query = re.sub(re.escape(wrong), correct, query, flags=re.IGNORECASE)
        
        # Expand contractions
        contractions = {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'re": " are", "'ve": " have", "'ll": " will", "'d": " would", "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            query = query.replace(contraction, expansion)
        
        # Clean up spacing
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    async def _check_immediate_responses(self, query: str) -> Optional[str]:
        """Check for immediate responses (time, date, basic greetings)"""
        query_lower = query.lower()
        
        # Time queries
        if any(phrase in query_lower for phrase in [
            'what time is it', 'current time', 'time now', 'what\'s the time',
            'tell me the time', 'time please'
        ]):
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            return f"🕐 **Current Time:** {time_str}\n📅 **Date:** {date_str}"
        
        # Date queries
        if any(phrase in query_lower for phrase in [
            'what date is it', 'today\'s date', 'current date', 'what day is it',
            'tell me the date', 'date please'
        ]):
            now = datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            day_str = now.strftime("%A")
            return f"📅 **Today is:** {day_str}\n📆 **Full Date:** {date_str}"
        
        return None
    
    async def _enhanced_nlp_analysis(self, query: str) -> Dict[str, Any]:
        """Enhanced NLP analysis using spaCy and custom processing"""
        try:
            # Use NLP engine for analysis
            nlp_result = await self.nlp_engine.analyze(query)
            
            # Convert NLPResult to dict and add custom analysis
            analysis = nlp_result.to_dict() if hasattr(nlp_result, 'to_dict') else {}
            
            # Add custom analysis
            analysis.update({
                'query_length': len(query),
                'word_count': len(query.split()),
                'has_question_mark': '?' in query,
                'is_greeting': any(word in query.lower() for word in ['hello', 'hi', 'hey', 'good morning']),
                'is_command': any(word in query.lower() for word in ['search', 'find', 'show', 'tell', 'get']),
                'is_question': any(word in query.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']),
                'mentions_time': any(word in query.lower() for word in ['time', 'date', 'when', 'today']),
                'mentions_jarvis': 'jarvis' in query.lower()
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"NLP analysis failed: {e}")
            return {'error': str(e)}
    
    async def _build_comprehensive_context(self, query: str, base_context: Optional[Dict], nlp_analysis: Dict) -> Dict[str, Any]:
        """Build comprehensive context with all available information"""
        context = base_context or {}
        
        # Add NLP analysis
        context['nlp_analysis'] = nlp_analysis
        
        # Add conversation memory
        context['conversation_history'] = list(self.conversation_memory)
        
        # Add personality settings
        context.update({
            'personality_mode': self.personality_mode,
            'user_name': self.user_name,
            'location': self.location,
            'learning_enabled': self.learning_enabled
        })
        
        # Add session info
        context.update({
            'active_quiz_id': self.active_quiz_id,
            'last_query': self.last_query,
            'last_response': self.last_response,
            'interaction_count': len(self.conversation_memory)
        })
        
        # Detect specific needs
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['search', 'find', 'look up', 'what is', 'who is']):
            context['needs_web_search'] = True
        
        if any(word in query_lower for word in ['bitcoin', 'currency', 'mutual fund', 'train', 'joke']):
            context['needs_api_data'] = True
        
        if any(word in query_lower for word in ['calculate', 'compute', 'solve', '+', '-', '*', '/']):
            context['needs_math'] = True
        
        return context
    
    async def _classify_intent_enhanced(self, query: str, context: Dict[str, Any]) -> Intent:
        """Enhanced intent classification with context awareness"""
        try:
            # Use enhanced intent classifier
            intent = await self.intent_classifier.classify(query, context)
            
            # Boost confidence based on context
            if context.get('nlp_analysis', {}).get('is_greeting') and intent.category.value == 'conversational':
                intent.confidence = min(intent.confidence + 0.2, 1.0)
            
            if context.get('needs_web_search') and intent.category.value == 'fetch':
                intent.confidence = min(intent.confidence + 0.15, 1.0)
            
            return intent
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return Intent(
                category=IntentCategory.QUESTION,
                confidence=0.5,
                parameters={},
                context=context
            )
    
    async def _route_and_process(self, query: str, intent: Intent, context: Dict[str, Any]) -> str:
        """Route query and process through appropriate handler"""
        
        # Check cache first
        cache_key = f"query_{hash(query)}_{intent.category.value}"
        cached_response = self.cache_manager.get(cache_key)
        if cached_response:
            logger.info("Using cached response")
            return cached_response
        
        # Route based on intent and context
        if context.get('needs_web_search'):
            response = await self._handle_web_search(query, context)
        elif context.get('needs_api_data'):
            response = await self._handle_api_data(query, context)
        elif context.get('needs_math'):
            response = await self._handle_math_query(query, context)
        elif intent.category.value == 'conversational':
            response = await self._handle_conversational(query, context)
        else:
            # Use intent router for complex routing
            response = await self.intent_router.route(query, intent, context)
        
        # Cache the response
        self.cache_manager.set(cache_key, response, ttl=1800)  # 30 minutes
        
        return response 
   
    async def _handle_web_search(self, query: str, context: Dict[str, Any]) -> str:
        """Handle web search queries"""
        try:
            # Extract search query
            search_query = query
            for keyword in ['search for', 'find', 'look up', 'what is', 'who is', 'tell me about']:
                if keyword in query.lower():
                    search_query = query.lower().split(keyword)[-1].strip()
                    break
            
            # Perform search and scrape
            web_results = await self.web_scraper.search_and_scrape(search_query, num_results=3)
            
            if web_results and not web_results.get('error') and web_results.get('scraped_content'):
                formatter = self.formatter_factory.get_formatter('web_search')
                return formatter.format(web_results)
            else:
                return f"I searched for '{search_query}' but couldn't find reliable information, sir. Would you like me to try a different approach?"
                
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"I encountered an issue while searching, sir. {str(e)}"
    
    async def _handle_api_data(self, query: str, context: Dict[str, Any]) -> str:
        """Handle API data queries (financial, railway, entertainment)"""
        try:
            query_lower = query.lower()
            
            # Financial data
            if any(keyword in query_lower for keyword in ['bitcoin', 'crypto', 'currency', 'mutual fund']):
                if 'bitcoin' in query_lower or 'crypto' in query_lower:
                    financial_data = await self.indian_api.get_financial_summary()
                    if not financial_data.get('error'):
                        formatter = self.formatter_factory.get_formatter('financial')
                        return formatter.format(financial_data)
                
                elif 'mutual fund' in query_lower:
                    mf_data = await self.indian_api.get_mutual_fund_info()
                    if not mf_data.get('error'):
                        formatter = self.formatter_factory.get_formatter('financial')
                        return formatter._format_mutual_funds(mf_data)
            
            # Railway data
            elif any(keyword in query_lower for keyword in ['train', 'railway', 'pnr']):
                railway_data = await self.indian_api.get_railway_info()
                if not railway_data.get('error'):
                    formatter = self.formatter_factory.get_formatter('railway')
                    return formatter.format(railway_data)
            
            # Entertainment
            elif any(keyword in query_lower for keyword in ['joke', 'quote', 'dog', 'cat']):
                content_type = 'joke'
                if 'quote' in query_lower:
                    content_type = 'quote'
                elif 'dog' in query_lower:
                    content_type = 'dog'
                elif 'cat' in query_lower:
                    content_type = 'cat'
                
                entertainment_data = await self.indian_api.get_entertainment(content_type)
                if not entertainment_data.get('error'):
                    formatter = self.formatter_factory.get_formatter('entertainment')
                    return formatter.format({'content': entertainment_data, 'type': content_type})
            
            return "I couldn't retrieve that information right now, sir. Please try again later."
            
        except Exception as e:
            logger.error(f"API data handling failed: {e}")
            return f"I encountered an issue accessing that data, sir. {str(e)}"
    
    async def _handle_math_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle mathematical queries"""
        try:
            # Extract mathematical expression
            expression = query
            for keyword in ['calculate', 'compute', 'solve', 'what is']:
                if keyword in query.lower():
                    expression = query.lower().split(keyword)[-1].strip()
                    break
            
            # Evaluate expression
            result = await self.math_engine.evaluate(expression)
            
            if result.get('success'):
                return f"The calculation yields: **{result['result']}**, sir."
            else:
                return f"I couldn't solve that mathematical expression, sir. {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Math query handling failed: {e}")
            return f"I encountered an issue with that calculation, sir. {str(e)}"
    
    async def _handle_conversational(self, query: str, context: Dict[str, Any]) -> str:
        """Handle conversational queries"""
        query_lower = query.lower()
        
        # Greetings
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            now = datetime.now()
            hour = now.hour
            
            if 5 <= hour < 12:
                return "Good morning, Mr. Stark. All systems are operational and ready for your commands."
            elif 12 <= hour < 17:
                return "Good afternoon, Mr. Stark. How may I be of service?"
            elif 17 <= hour < 21:
                return "Good evening, Mr. Stark. How was your day?"
            else:
                return "Working late again, Mr. Stark? I'm here to assist."
        
        # Capability questions
        elif any(phrase in query_lower for phrase in ['what can you do', 'how can you help', 'what are your capabilities']):
            return """I can assist you with a wide range of tasks, sir:

🔍 **Web Search & Information Retrieval**
💰 **Financial Data** (Bitcoin prices, currency rates, mutual funds)
🚂 **Indian Railway Information** 
🎭 **Entertainment** (jokes, quotes, images)
⏰ **Time & Date Information**
🧮 **Mathematical Calculations**
💬 **Natural Conversations**
🎯 **Proactive Assistance**

How may I assist you today, Mr. Stark?"""
        
        # Identity questions
        elif any(phrase in query_lower for phrase in ['who are you', 'what are you']):
            return "I am JARVIS - Just A Rather Very Intelligent System. Your personal AI assistant, Mr. Stark. I'm here to help you with information, calculations, research, and whatever else you might need."
        
        # Status questions
        elif any(phrase in query_lower for phrase in ['how are you', 'status', 'are you okay']):
            return "All systems operational and running at optimal efficiency, sir. Ready to assist with whatever you need."
        
        # Thanks
        elif any(word in query_lower for word in ['thank', 'thanks']):
            return "You're most welcome, sir. Always happy to assist."
        
        # Default conversational response
        else:
            return "I'm here to help, Mr. Stark. What can I do for you?"
    
    async def _apply_iron_man_personality(self, response: str, query: str) -> str:
        """Apply Iron Man JARVIS personality to response"""
        # Add sir/Mr. Stark if not present
        if 'sir' not in response.lower() and 'mr. stark' not in response.lower():
            # Add sir to the end if it's a short response
            if len(response.split()) < 10:
                response = response.rstrip('.') + ', sir.'
        
        # Ensure proper capitalization
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        return response
    
    async def _update_memory_and_learning(self, query: str, response: str):
        """Update memory and learning systems"""
        # Add to conversation memory
        self.conversation_memory.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update last query/response
        self.last_query = query
        self.last_response = response
        
        # Add to training data for learning
        self.training_data.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    async def _generate_iron_man_error_response(self, error: str) -> str:
        """Generate Iron Man style error response"""
        error_responses = [
            f"I apologize, sir. I encountered a technical difficulty: {error}",
            f"My systems experienced an issue, Mr. Stark: {error}",
            f"There seems to be a glitch in my processing, sir: {error}",
            f"I'm experiencing some interference, Mr. Stark: {error}"
        ]
        
        import random
        return random.choice(error_responses)
    
    def get_memory(self) -> List[Dict[str, Any]]:
        """Get conversation memory."""
        return list(self.conversation_memory)
    
    def clear_memory(self):
        """Clear conversation memory and history."""
        self.conversation_memory.clear()
        self.training_data.clear()
        self.last_query = None
        self.last_response = None
        logger.info("Jarvis memory cleared")
    
    async def generate_greeting(self) -> str:
        """Generate Jarvis greeting for Heoster."""
        return self.heoster_personality.get_greeting()
    
    async def generate_farewell(self) -> str:
        """Generate Jarvis farewell for Heoster."""
        return self.heoster_personality.farewell()
    
    def get_status(self) -> Dict[str, Any]:
        """Get Jarvis brain status for Heoster."""
        return {
            'name': 'Jarvis',
            'owner': self.heoster_personality.owner,
            'developer': self.heoster_personality.company,
            'version': self.heoster_personality.version,
            'model': self.model_name,
            'transformer_loaded': self.model is not None,
            'langchain_enabled': self.conversation_chain is not None,
            'api_routing_enabled': self.api_router is not None,
            'web_scraping_enabled': self.web_scraper is not None,
            'active_quiz': self.active_quiz_id is not None,
            'memory_size': len(self.conversation_memory),
            'temperature': self.temperature,
            'max_length': self.max_length,
            'status': 'operational' if self.model else 'limited',
            'features': [
                'Iron Man Personality',
                'Advanced Web Search & Scraping',
                'Real-time Data Gathering',
                'Smart Query Preprocessing',
                'Enhanced NLP Analysis',
                'Automatic Learning',
                'Time/Date Awareness',
                'Mathematical Calculations',
                'Conversational AI',
                'Personal AI for Heoster'
            ]
        }
    
    async def process_feedback(self, query: str, response: str, feedback: str) -> bool:
        """
        Process user feedback and trigger learning if positive
        
        Args:
            query: Original query
            response: JARVIS response
            feedback: User feedback
            
        Returns:
            True if learning was triggered
        """
        try:
            # Check if feedback is positive
            positive_indicators = ['good', 'great', 'excellent', 'perfect', 'correct', 'right', 'yes', 'thanks']
            is_positive = any(indicator in feedback.lower() for indicator in positive_indicators)
            
            if is_positive:
                self.positive_feedback_count += 1
                logger.info(f"Positive feedback received. Count: {self.positive_feedback_count}")
                
                # Trigger learning if threshold reached
                if self.positive_feedback_count >= self.learning_threshold:
                    logger.info("Learning threshold reached. Updating knowledge base.")
                    self.positive_feedback_count = 0  # Reset counter
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
            return False
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced status with all new features"""
        base_status = self.get_status()
        
        # Add Iron Man features
        base_status.update({
            'iron_man_mode': True,
            'knowledge_integration': True,
            'automatic_training': True,
            'smart_editing': True,
            'time_awareness': True,
            'enhanced_features': [
                'Iron Man Personality',
                'Smart Knowledge Integration', 
                'Automatic Learning',
                'Smart Query Editing',
                'Time/Date Awareness',
                'Proactive Assistance',
                'Enhanced Conversational AI',
                'Advanced NLP Processing',
                'Intent Classification',
                'Response Formatting',
                'Cache Management',
                'Metrics Collection'
            ],
            'training_stats': {
                'positive_feedback_count': self.positive_feedback_count,
                'learning_threshold': self.learning_threshold,
                'training_data_size': len(self.training_data),
                'conversation_memory_size': len(self.conversation_memory)
            }
        })
        
        return base_status