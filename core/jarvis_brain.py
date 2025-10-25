"""Jarvis Brain - Advanced response generation using Transformers + LangChain."""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.logger import get_logger
from core.api_router import get_api_router, APIEndpoint
from core.heoster_personality import get_heoster_jarvis
from core.web_scraper import get_web_scraper
from core.indian_apis import get_indian_api
from core.conversation_handler import get_conversation_handler

logger = get_logger(__name__)


class JarvisBrain:
    """
    Jarvis's intelligent brain combining Transformers and LangChain.
    Generates sophisticated, context-aware responses.
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
        
        logger.info("Jarvis Brain initialized with Natural Language Understanding + Transformers + LangChain + APIs")
        logger.info(f"Personal AI for {self.heoster_personality.owner}, developed by {self.heoster_personality.company}")
        logger.info("Enhanced conversational abilities and Indian-specific features enabled")
    
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
Hu
man: {input}
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
        Generate intelligent response using Transformers + LangChain + API Routing + Web Scraping.
        
        Args:
            query: User query
            context: Additional context (real-time data, execution results, etc.)
            
        Returns:
            Jarvis's response
        """
        try:
            # Initialize web scraper if needed
            if self.web_scraper is None:
                self.web_scraper = await get_web_scraper()
            
            # Initialize Indian API if needed
            if self.indian_api is None:
                self.indian_api = await get_indian_api()
            
            # Initialize context if not provided
            if context is None:
                context = {}
            
            # First, check if we're awaiting clarification
            if self.conversation_handler.awaiting_clarification:
                clarification_response = self.conversation_handler.handle_clarification_response(query)
                if clarification_response:
                    # If it's a selection, continue processing
                    if "Let me help you with that" in clarification_response:
                        logger.info("User provided clarification, continuing...")
                        # Add to history and continue
                        self.conversation_handler.add_to_history(query, clarification_response)
                    else:
                        # Return clarification response
                        self.conversation_handler.add_to_history(query, clarification_response)
                        return clarification_response
            
            # Try to understand the query using conversation handler
            understanding = self.conversation_handler.understand_query(query)
            logger.info(f"Query understanding: intent={understanding.get('intent')}, type={understanding.get('query_type')}, confidence={understanding.get('confidence')}")
            
            # Check if clarification is needed
            if self.conversation_handler.should_ask_clarification(query, understanding):
                is_ambiguous, options = self.conversation_handler.detect_ambiguity(query, understanding)
                
                if is_ambiguous:
                    # Generate suggestions if no specific options
                    if not options or options == ['Please be more specific about what you need']:
                        options = self.conversation_handler.generate_suggestions(query)
                    
                    clarification_question = self.conversation_handler.generate_clarification_question(query, options)
                    self.conversation_handler.awaiting_clarification = True
                    self.conversation_handler.clarification_options = options
                    
                    logger.info(f"Asking for clarification with {len(options)} options")
                    self.conversation_handler.add_to_history(query, clarification_question)
                    return clarification_question
            
            # Check for conversational intents (greetings, thanks, etc.)
            if understanding.get('intent') and understanding.get('confidence', 0) > 0.7:
                contextual_response = self.conversation_handler.generate_contextual_response(query, understanding)
                if contextual_response:
                    logger.info(f"Using conversational response for intent: {understanding.get('intent')}")
                    self.last_query = query
                    self.last_response = contextual_response
                    self._update_memory(query, contextual_response)
                    self.conversation_handler.add_to_history(query, contextual_response, understanding.get('intent'))
                    return contextual_response
            
            # Check if query requires Indian financial/geographical data
            indian_finance_keywords = ['bitcoin', 'crypto', 'btc', 'currency', 'exchange rate', 'inr', 'rupee', 'dollar', 'euro']
            indian_geo_keywords = ['muzaffarnagar', 'pincode', 'pin code', '251201', 'uttar pradesh', 'up', 'my location', 'ip address']
            railway_keywords = ['train', 'railway', 'pnr', 'irctc', 'train schedule', 'train number']
            mutual_fund_keywords = ['mutual fund', 'nav', 'sbi bluechip', 'hdfc', 'icici', 'scheme code', 'fund house']
            entertainment_keywords = ['joke', 'funny', 'dog image', 'cat fact', 'quote', 'inspire me', 'make me laugh']
            
            needs_indian_finance = any(keyword in query.lower() for keyword in indian_finance_keywords)
            needs_indian_geo = any(keyword in query.lower() for keyword in indian_geo_keywords)
            needs_railway = any(keyword in query.lower() for keyword in railway_keywords)
            needs_mutual_fund = any(keyword in query.lower() for keyword in mutual_fund_keywords)
            needs_entertainment = any(keyword in query.lower() for keyword in entertainment_keywords)
            
            # Handle Indian Railway queries
            if needs_railway:
                logger.info(f"🚂 Query requires Indian Railway data: '{query}'")
                railway_data = await self.indian_api.get_railway_info()
                
                if not railway_data.get('error'):
                    formatted_railway = self._format_indian_railway(railway_data)
                    self.last_query = query
                    self.last_response = formatted_railway
                    self._update_memory(query, formatted_railway)
                    return formatted_railway
            
            # Handle Mutual Fund queries
            if needs_mutual_fund:
                logger.info(f"📈 Query requires Mutual Fund data: '{query}'")
                mf_data = await self.indian_api.get_mutual_fund_info()
                
                if not mf_data.get('error'):
                    formatted_mf = self._format_mutual_fund(mf_data)
                    self.last_query = query
                    self.last_response = formatted_mf
                    self._update_memory(query, formatted_mf)
                    return formatted_mf
            
            # Handle Entertainment queries
            if needs_entertainment:
                logger.info(f"😄 Query requires Entertainment content: '{query}'")
                
                # Determine content type
                content_type = 'joke'
                if 'programming' in query.lower() or 'code' in query.lower():
                    content_type = 'programming_joke'
                elif 'dog' in query.lower():
                    content_type = 'dog'
                elif 'cat' in query.lower():
                    content_type = 'cat'
                elif 'quote' in query.lower() or 'inspire' in query.lower():
                    content_type = 'quote'
                
                entertainment_data = await self.indian_api.get_entertainment(content_type)
                
                if not entertainment_data.get('error'):
                    formatted_entertainment = self._format_entertainment(entertainment_data, content_type)
                    self.last_query = query
                    self.last_response = formatted_entertainment
                    self._update_memory(query, formatted_entertainment)
                    return formatted_entertainment
            
            # Handle Indian financial queries
            if needs_indian_finance:
                logger.info(f"💰 Query requires Indian financial data: '{query}'")
                financial_data = await self.indian_api.get_financial_summary()
                
                if not financial_data.get('error'):
                    formatted_finance = self._format_indian_finance(financial_data)
                    self.last_query = query
                    self.last_response = formatted_finance
                    self._update_memory(query, formatted_finance)
                    return formatted_finance
            
            # Handle Indian geographical queries
            if needs_indian_geo:
                logger.info(f"📍 Query requires Indian geographical data: '{query}'")
                location_data = await self.indian_api.get_location_summary()
                
                if not location_data.get('error'):
                    formatted_location = self._format_indian_location(location_data)
                    self.last_query = query
                    self.last_response = formatted_location
                    self._update_memory(query, formatted_location)
                    return formatted_location
            
            # Check if query requires web search/scraping
            web_search_keywords = ['search', 'find', 'look up', 'what is', 'who is', 'latest', 'news about', 'information on', 'tell me about']
            needs_web_search = any(keyword in query.lower() for keyword in web_search_keywords)
            
            # If web search is needed, perform it first
            if needs_web_search and not context.get('skip_web_search'):
                logger.info(f"🔍 Query requires web search: '{query}'")
                
                # Extract search query
                search_query = query
                for keyword in ['search for', 'find', 'look up', 'what is', 'who is', 'tell me about', 'information on']:
                    if keyword in query.lower():
                        search_query = query.lower().split(keyword)[-1].strip()
                        logger.info(f"📝 Extracted search query: '{search_query}'")
                        break
                
                # Perform search and scrape
                logger.info(f"🌐 Performing web search and scrape for: '{search_query}'")
                web_results = await self.web_scraper.search_and_scrape(search_query, num_results=3)
                
                # Log results
                if web_results:
                    scraped_count = len(web_results.get('scraped_content', []))
                    logger.info(f"✅ Web search complete: {scraped_count} pages scraped")
                
                # If we got results, format and return them directly
                if web_results and not web_results.get('error') and web_results.get('scraped_content'):
                    logger.info("📄 Formatting web search results for display")
                    formatted_results = self._format_web_search_results(web_results)
                    
                    # Store in memory
                    self.last_query = query
                    self.last_response = formatted_results
                    self._update_memory(query, formatted_results)
                    
                    logger.info("✅ Returning formatted web search results")
                    return formatted_results
                else:
                    logger.warning(f"⚠️ Web search returned no scraped content")
                
                # Add web results to context for fallback
                context['web_search_results'] = web_results
                context['web_search_performed'] = True
            
            # First, check if this should be routed to a specific API endpoint
            api_context = {
                'active_quiz_id': self.active_quiz_id,
                'last_query': self.last_query,
                'last_response': self.last_response
            }
            
            api_result = await self.api_router.route_request(query, api_context)
            
            if api_result.get('routed'):
                # API endpoint handled the request
                response = api_result.get('formatted', 'Request processed.')
                
                # Update quiz state if applicable
                if api_result.get('type') == 'quiz_create':
                    self.active_quiz_id = api_result.get('quiz_id')
                elif api_result.get('type') == 'quiz_answer':
                    if api_result.get('completed'):
                        self.active_quiz_id = None
                
                # Store in memory
                self.last_query = query
                self.last_response = response
                self._update_memory(query, response)
                
                return response
            # Check for simple conversational intents first (greetings, thanks, etc.)
            # Use fallback for these to ensure consistent, appropriate responses
            if context and context.get('intent'):
                intent = context['intent']
                intent_context = intent.context
                if 'preprocessed' in intent_context:
                    preprocessed = intent_context['preprocessed']
                    detected_intent = preprocessed.get('intent')
                    
                    # Use fallback for simple conversational intents
                    if detected_intent in ['greeting', 'farewell', 'thanks']:
                        return self._generate_fallback_response(query, context)
                    
                    # Use fallback for math queries with execution results
                    if detected_intent == 'math' and context.get('execution_results'):
                        return self._generate_fallback_response(query, context)
                    
                    # Use fallback for questions and other queries
                    if detected_intent in ['question', 'weather', 'news', 'search']:
                        return self._generate_fallback_response(query, context)
            
            # Build enhanced prompt with context
            enhanced_query = self._build_enhanced_prompt(query, context)
            
            # Generate response using LangChain if available
            if self.conversation_chain:
                response = await asyncio.to_thread(
                    self.conversation_chain.predict,
                    input=enhanced_query
                )
            else:
                # Fallback to direct transformer generation
                response = await self._generate_with_transformer(enhanced_query)
            
            # Post-process response
            response = self._post_process_response(response, context)
            
            # Store in memory
            self.last_query = query
            self.last_response = response
            self._update_memory(query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Jarvis response generation failed: {e}")
            return self._generate_fallback_response(query, context)
    
    def _build_enhanced_prompt(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build enhanced prompt with context including web search results."""
        # Use Heoster's personal Jarvis system prompt
        prompt_parts = [
            self.heoster_personality.create_system_prompt(),
            f"\nHeoster's Query: {query}"
        ]
        
        if not context:
            return "\n".join(prompt_parts)
        
        # Add web search results if available
        if context.get('web_search_results'):
            web_results = context['web_search_results']
            if not web_results.get('error') and web_results.get('scraped_content'):
                prompt_parts.append("\nWeb Search Results:")
                for i, item in enumerate(web_results['scraped_content'][:3], 1):
                    prompt_parts.append(f"\n{i}. {item['title']}")
                    prompt_parts.append(f"   URL: {item['url']}")
                    prompt_parts.append(f"   Content: {item['content'][:500]}...")
                prompt_parts.append("\nUse this information to provide an accurate, comprehensive response to Heoster.")
        
        # Add real-time data context with rich information
        if context.get('realtime_data'):
            realtime = context['realtime_data']
            
            if 'weather' in realtime and not realtime['weather'].get('error'):
                weather = realtime['weather']
                prompt_parts.append(
                    f"\nWeather Information: The current temperature in {weather.get('location', 'the area')} "
                    f"is {weather.get('temperature', 'N/A')}°C with {weather.get('description', 'unknown conditions')}. "
                    f"Humidity is {weather.get('humidity', 'N/A')}%."
                )
            
            if 'news' in realtime and realtime['news']:
                news_items = [n for n in realtime['news'] if not n.get('error')]
                if news_items:
                    prompt_parts.append(f"\nLatest News Headlines:")
                    for i, article in enumerate(news_items[:3], 1):
                        prompt_parts.append(f"{i}. {article.get('title', 'N/A')} - {article.get('source', 'Unknown')}")
            
            if 'search' in realtime and realtime['search']:
                search_results = [s for s in realtime['search'] if not s.get('error')]
                if search_results:
                    prompt_parts.append(f"\nWeb Search Results:")
                    for i, result in enumerate(search_results[:3], 1):
                        prompt_parts.append(f"{i}. {result.get('title', 'N/A')}: {result.get('snippet', 'N/A')[:100]}")
            
            if 'knowledge' in realtime and not realtime['knowledge'].get('error'):
                knowledge = realtime['knowledge']
                prompt_parts.append(
                    f"\nKnowledge Base: {knowledge.get('title', 'Information')}\n"
                    f"{knowledge.get('summary', 'No summary available')[:300]}"
                )
        
        # Add execution results with context
        if context.get('execution_results'):
            results = context['execution_results']
            if results.get('success'):
                prompt_parts.append(f"\nComputation Result: {results.get('result', 'Success')}")
        
        prompt_parts.append("\nProvide a clear, helpful response based on the above information:")
        
        return "\n".join(prompt_parts)
    
    async def _generate_with_transformer(self, prompt: str) -> str:
        """Generate response using transformer model directly."""
        if not self.model or not self.tokenizer:
            return "I apologize, but my systems are not fully operational."
        
        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            outputs = await asyncio.to_thread(
                self.model.generate,
                **inputs,
                max_length=self.max_length,
                num_beams=5,
                temperature=self.temperature,
                do_sample=True,
                top_p=0.9,
                early_stopping=True
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
            
        except Exception as e:
            logger.error(f"Transformer generation failed: {e}")
            return "I encountered a processing error. Please try again."
    
    def _post_process_response(
        self,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Post-process and enhance response."""
        # Remove any prompt artifacts
        response = response.strip()
        
        # Add Jarvis personality touches
        if context and context.get('confidence', 1.0) < 0.5:
            response = f"I believe {response.lower()}"
        
        # Ensure proper capitalization
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        # Add period if missing
        if response and response[-1] not in '.!?':
            response += '.'
        
        return response
    
    def _generate_fallback_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate intelligent fallback response when main generation fails."""
        # First try conversation handler
        understanding = self.conversation_handler.understand_query(query)
        if understanding.get('intent'):
            contextual_response = self.conversation_handler.generate_contextual_response(query, understanding)
            if contextual_response:
                return contextual_response
        
        query_lower = query.lower().strip()
        
        # Check if we have preprocessed/normalized text in context
        if context and context.get('intent'):
            intent_context = context['intent'].context
            if 'preprocessed' in intent_context:
                preprocessed = intent_context['preprocessed']
                # Use normalized text for better matching
                query_lower = preprocessed.get('normalized', query_lower).lower()
                
                # Use detected intent for direct responses
                detected_intent = preprocessed.get('intent')
                if detected_intent == 'greeting':
                    from datetime import datetime
                    hour = datetime.now().hour
                    if hour < 12:
                        return "Good morning, sir. Jarvis at your service. How may I assist you today?"
                    elif hour < 18:
                        return "Good afternoon, sir. Jarvis at your service. How may I assist you today?"
                    else:
                        return "Good evening, sir. Jarvis at your service. How may I assist you today?"
                elif detected_intent == 'farewell':
                    return "Until next time, sir. Don't hesitate to call if you need assistance."
                elif detected_intent == 'thanks':
                    return "You're most welcome, sir. I'm here whenever you need assistance."
        
        # Handle very short or unclear inputs
        if len(query_lower) <= 2:
            return "I didn't quite catch that, sir. Could you please be more specific?"
        
        # Greeting responses (with fuzzy matching)
        greeting_patterns = ['hello', 'hi', 'hey', 'greetings', 'hlo', 'hii', 'hy']
        if any(pattern in query_lower for pattern in greeting_patterns):
            from datetime import datetime
            hour = datetime.now().hour
            if hour < 12:
                return "Good morning, sir. Jarvis at your service. How may I assist you today?"
            elif hour < 18:
                return "Good afternoon, sir. Jarvis at your service. How may I assist you today?"
            else:
                return "Good evening, sir. Jarvis at your service. How may I assist you today?"
        
        # Math queries
        if any(word in query_lower for word in ['calculate', 'what is', '+', '-', '*', '/', 'solve']):
            if context and context.get('execution_results'):
                result = context['execution_results'].get('result')
                if result:
                    return f"The calculation yields {result}."
            return "I can help you with mathematical calculations. Please provide the expression you'd like me to compute."
        
        # Weather queries
        if 'weather' in query_lower:
            if context and context.get('realtime_data', {}).get('weather'):
                weather = context['realtime_data']['weather']
                if not weather.get('error'):
                    return (
                        f"The current weather in {weather.get('location', 'your area')} shows "
                        f"{weather.get('temperature', 'N/A')}°C with {weather.get('description', 'unknown conditions')}. "
                        f"Humidity is at {weather.get('humidity', 'N/A')}%."
                    )
            return "I can provide weather information. Please specify a location, or configure your weather API key."
        
        # News queries
        if 'news' in query_lower:
            if context and context.get('realtime_data', {}).get('news'):
                news = context['realtime_data']['news']
                if news and not news[0].get('error'):
                    headlines = "\n".join([f"- {article.get('title', 'N/A')}" for article in news[:3]])
                    return f"Here are the latest headlines:\n{headlines}"
            return "I can fetch the latest news for you. Please configure your news API key for this feature."
        
        # Search queries
        if any(word in query_lower for word in ['search', 'find', 'look up']):
            if context and context.get('realtime_data', {}).get('search'):
                results = context['realtime_data']['search']
                if results and not results[0].get('error'):
                    return f"I found {len(results)} relevant results. The top result is: {results[0].get('title', 'N/A')}"
            return "I can search the web for information. What would you like me to find?"
        
        # Knowledge queries
        if any(word in query_lower for word in ['who is', 'what is', 'tell me about', 'explain']):
            if context and context.get('realtime_data', {}).get('knowledge'):
                knowledge = context['realtime_data']['knowledge']
                if not knowledge.get('error'):
                    return f"{knowledge.get('title', 'Information')}: {knowledge.get('summary', 'No information available')[:200]}..."
            return "I can provide information on various topics. What would you like to know about?"
        
        # Thank you responses
        if any(word in query_lower for word in ['thank', 'thanks']):
            return "You're welcome, sir. I'm here whenever you need assistance."
        
        # Goodbye responses
        if any(word in query_lower for word in ['bye', 'goodbye', 'see you']):
            return "Until next time, sir. Don't hesitate to call if you need assistance."
        
        # Default intelligent fallback
        return "I'm here to assist you with calculations, information lookup, web searches, and various other tasks. How may I help you today?"
    
    def _format_web_search_results(self, web_results: Dict[str, Any]) -> str:
        """
        Format web search results for display to Heoster
        
        Args:
            web_results: Dictionary with search and scraped results
        
        Returns:
            Formatted string with search results
        """
        query = web_results.get('query', '')
        scraped_content = web_results.get('scraped_content', [])
        search_results = web_results.get('search_results', [])
        
        if not scraped_content and not search_results:
            return self.heoster_personality.format_response(
                f"I searched for '{query}' but couldn't retrieve any results, sir.",
                'error'
            )
        
        # Build comprehensive response with clear formatting
        response = f"\n{'='*80}\n"
        response += f"🔍 SEARCH RESULTS FOR: '{query}'\n"
        response += f"{'='*80}\n\n"
        
        # If we have scraped content, show it with full details
        if scraped_content:
            response += f"✅ Successfully scraped {len(scraped_content)} pages with detailed content:\n\n"
            
            for i, item in enumerate(scraped_content, 1):
                response += f"\n{'─'*80}\n"
                response += f"📄 RESULT #{i}\n"
                response += f"{'─'*80}\n\n"
                
                # Title (bold and prominent)
                title = item.get('title', 'No title')
                response += f"TITLE: {title}\n\n"
                
                # Extract domain name from URL
                url = item.get('url', 'N/A')
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                    # Remove 'www.' prefix if present
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    website_name = domain if domain else 'Unknown'
                except:
                    website_name = 'Unknown'
                
                response += f"🌐 SOURCE: {website_name}\n\n"
                
                # Search snippet
                if item.get('snippet'):
                    snippet = item['snippet']
                    response += f"📝 SEARCH SUMMARY:\n{snippet}\n\n"
                
                # Meta description if available
                if item.get('description') and item['description'] != item.get('snippet'):
                    response += f"📋 PAGE DESCRIPTION:\n{item['description']}\n\n"
                
                # Main scraped content with headings preserved
                if item.get('content'):
                    content = item['content'].strip()
                    
                    # Show substantial content (up to 1500 chars for better visibility)
                    display_content = content[:1500]
                    if len(content) > 1500:
                        display_content += "..."
                    
                    response += f"📖 SCRAPED CONTENT:\n"
                    response += f"{'-'*80}\n"
                    response += f"{display_content}\n"
                    response += f"{'-'*80}\n"
                    response += f"(Showing {len(display_content)} of {len(content)} characters)\n\n"
                
                # Show we have more content available
                if item.get('full_content'):
                    full_len = len(item['full_content'])
                    response += f"💾 Full content available: {full_len} characters total\n"
        
        # If we only have search results without scraped content
        elif search_results:
            response += f"📋 Found {len(search_results)} search results:\n\n"
            
            for i, item in enumerate(search_results[:5], 1):
                response += f"\n{i}. {item.get('title', 'No title')}\n"
                
                # Extract domain name from URL
                url = item.get('url', 'N/A')
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    website_name = domain if domain else 'Unknown'
                except:
                    website_name = 'Unknown'
                
                response += f"   🌐 {website_name}\n"
                if item.get('snippet'):
                    response += f"   📝 {item['snippet'][:200]}\n"
                response += "\n"
        
        # Summary footer
        response += f"\n{'='*80}\n"
        response += f"✅ SEARCH COMPLETE\n"
        response += f"{'='*80}\n\n"
        
        if scraped_content:
            response += f"I've retrieved and analyzed {len(scraped_content)} web pages for you, sir.\n"
            response += "The content above includes the actual text scraped from each page.\n\n"
        
        response += "Would you like me to:\n"
        response += "• Search for more specific information?\n"
        response += "• Explore any of these sources in more detail?\n"
        response += "• Summarize the key points from these results?\n"
        
        return response
    
    def _format_indian_finance(self, financial_data: Dict[str, Any]) -> str:
        """Format Indian financial data for display"""
        response = f"\n{'='*80}\n"
        response += f"💰 INDIAN FINANCIAL DATA (INR)\n"
        response += f"{'='*80}\n\n"
        
        # Cryptocurrency
        if 'cryptocurrency' in financial_data and not financial_data['cryptocurrency'].get('error'):
            crypto = financial_data['cryptocurrency']
            response += f"📊 CRYPTOCURRENCY PRICES\n"
            response += f"{'-'*80}\n"
            response += f"Bitcoin (BTC):\n"
            response += f"  • Price in INR: ₹{crypto.get('price_inr', 'N/A'):,.2f}\n"
            response += f"  • Price in USD: ${crypto.get('price_usd', 'N/A'):,.2f}\n"
            response += f"  • Last Updated: {crypto.get('updated', 'N/A')}\n\n"
        
        # Currency Rates
        if 'currency_rates' in financial_data and not financial_data['currency_rates'].get('error'):
            rates = financial_data['currency_rates']
            response += f"💱 CURRENCY EXCHANGE RATES (Base: INR)\n"
            response += f"{'-'*80}\n"
            for currency, rate in rates.get('rates', {}).items():
                response += f"  • 1 INR = {rate} {currency}\n"
            response += f"  • Updated: {rates.get('updated', 'N/A')}\n\n"
        
        response += f"{'='*80}\n"
        response += f"✅ Financial data for India\n"
        response += f"{'='*80}\n"
        
        return response
    
    def _format_indian_location(self, location_data: Dict[str, Any]) -> str:
        """Format Indian geographical data for display"""
        response = f"\n{'='*80}\n"
        response += f"📍 INDIAN GEOGRAPHICAL DATA\n"
        response += f"{'='*80}\n\n"
        
        # Pincode Info
        if 'pincode_info' in location_data and not location_data['pincode_info'].get('error'):
            pincode = location_data['pincode_info']
            response += f"📮 PINCODE INFORMATION\n"
            response += f"{'-'*80}\n"
            response += f"PIN Code: {pincode.get('pincode', 'N/A')}\n"
            response += f"Place: {pincode.get('place_name', 'N/A')}\n"
            response += f"State: {pincode.get('state', 'N/A')}\n"
            response += f"Coordinates: {pincode.get('latitude', 'N/A')}, {pincode.get('longitude', 'N/A')}\n"
            response += f"Country: {pincode.get('country', 'N/A')}\n\n"
        
        # IP Location
        if 'your_location' in location_data and not location_data['your_location'].get('error'):
            ip_loc = location_data['your_location']
            response += f"🌐 YOUR CURRENT LOCATION (Based on IP)\n"
            response += f"{'-'*80}\n"
            response += f"IP Address: {ip_loc.get('ip', 'N/A')}\n"
            response += f"City: {ip_loc.get('city', 'N/A')}\n"
            response += f"Region: {ip_loc.get('region', 'N/A')}\n"
            response += f"Country: {ip_loc.get('country', 'N/A')}\n"
            response += f"Postal Code: {ip_loc.get('postal', 'N/A')}\n"
            response += f"Currency: {ip_loc.get('currency', 'N/A')}\n\n"
        
        response += f"{'='*80}\n"
        response += f"✅ Default Location: {location_data.get('default_location', 'Muzaffarnagar, UP, India')}\n"
        response += f"{'='*80}\n"
        
        return response
    
    def _format_indian_railway(self, railway_data: Dict[str, Any]) -> str:
        """Format Indian Railway data for display"""
        response = f"\n{'='*80}\n"
        response += f"🚂 INDIAN RAILWAY INFORMATION\n"
        response += f"{'='*80}\n\n"
        
        if 'train_number' in railway_data:
            response += f"🚆 TRAIN DETAILS\n"
            response += f"{'-'*80}\n"
            response += f"Train Number: {railway_data.get('train_number', 'N/A')}\n"
            response += f"Train Name: {railway_data.get('train_name', 'N/A')}\n"
            response += f"Route: {railway_data.get('route', 'N/A')}\n"
            response += f"Departure: {railway_data.get('departure_time', 'N/A')}\n"
            response += f"Arrival: {railway_data.get('arrival_time', 'N/A')}\n"
            response += f"Running Days: {railway_data.get('running_days', 'N/A')}\n\n"
        
        if 'popular_trains_from_muzaffarnagar' in railway_data:
            response += f"🚉 POPULAR TRAINS FROM MUZAFFARNAGAR\n"
            response += f"{'-'*80}\n"
            for train in railway_data['popular_trains_from_muzaffarnagar']:
                response += f"  • Train {train}\n"
            response += "\n"
        
        if 'note' in railway_data:
            response += f"ℹ️  Note: {railway_data['note']}\n"
        
        response += f"{'='*80}\n"
        response += f"✅ Railway information for Muzaffarnagar, UP\n"
        response += f"{'='*80}\n"
        
        return response
    
    def _format_mutual_fund(self, mf_data: Dict[str, Any]) -> str:
        """Format Mutual Fund data for display"""
        response = f"\n{'='*80}\n"
        response += f"📈 INDIAN MUTUAL FUND NAV\n"
        response += f"{'='*80}\n\n"
        
        if 'scheme_name' in mf_data:
            response += f"💼 FUND DETAILS\n"
            response += f"{'-'*80}\n"
            response += f"Scheme Name: {mf_data.get('scheme_name', 'N/A')}\n"
            response += f"Scheme Code: {mf_data.get('scheme_code', 'N/A')}\n"
            response += f"Fund House: {mf_data.get('fund_house', 'N/A')}\n"
            response += f"Scheme Type: {mf_data.get('scheme_type', 'N/A')}\n"
            response += f"NAV: ₹{mf_data.get('nav', 'N/A')}\n"
            response += f"Date: {mf_data.get('date', 'N/A')}\n"
            response += f"Currency: {mf_data.get('currency', 'INR')}\n\n"
        
        if 'matches' in mf_data:
            response += f"🔍 SEARCH RESULTS\n"
            response += f"{'-'*80}\n"
            for match in mf_data['matches']:
                response += f"  • {match['name']} (Code: {match['code']})\n"
            response += "\n"
        
        if 'popular_funds' in mf_data:
            response += f"⭐ POPULAR MUTUAL FUNDS\n"
            response += f"{'-'*80}\n"
            for fund in mf_data['popular_funds']:
                response += f"  • {fund['name']} (Code: {fund['code']})\n"
            response += "\n"
        
        response += f"{'='*80}\n"
        response += f"✅ Mutual Fund data from AMFI (India)\n"
        response += f"{'='*80}\n"
        
        return response
    
    def _format_entertainment(self, entertainment_data: Dict[str, Any], content_type: str) -> str:
        """Format Entertainment content for display"""
        response = f"\n{'='*80}\n"
        
        if content_type in ['joke', 'programming_joke']:
            response += f"😄 RANDOM JOKE\n"
            response += f"{'='*80}\n\n"
            response += f"Type: {entertainment_data.get('type', 'general').title()}\n\n"
            response += f"🎭 {entertainment_data.get('setup', '')}\n\n"
            response += f"😂 {entertainment_data.get('punchline', '')}\n\n"
        
        elif content_type == 'dog':
            response += f"🐕 RANDOM DOG IMAGE\n"
            response += f"{'='*80}\n\n"
            response += f"Image URL: {entertainment_data.get('image_url', 'N/A')}\n\n"
            response += f"Enjoy this cute dog! 🐶\n\n"
        
        elif content_type == 'cat':
            response += f"🐱 RANDOM CAT FACT\n"
            response += f"{'='*80}\n\n"
            response += f"Did you know?\n\n"
            response += f"🐈 {entertainment_data.get('fact', 'N/A')}\n\n"
            response += f"Upvotes: {entertainment_data.get('upvotes', 0)} 👍\n\n"
        
        elif content_type == 'quote':
            response += f"💭 INSPIRATIONAL QUOTE\n"
            response += f"{'='*80}\n\n"
            response += f'"{entertainment_data.get("quote", "N/A")}"\n\n'
            response += f"— {entertainment_data.get('author', 'Unknown')}\n\n"
        
        response += f"{'='*80}\n"
        
        return response
    
    def _update_memory(self, query: str, response: str):
        """Update conversation memory and history."""
        self.memory.append({
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'response': response
        })
        
        # Also update conversation handler history
        self.conversation_handler.add_to_history(query, response)
        
        # Keep only last 10 exchanges in memory
        if len(self.memory) > 10:
            self.memory = self.memory[-10:]
    
    def get_memory(self) -> List[Dict[str, Any]]:
        """Get conversation memory."""
        return self.memory
    
    def clear_memory(self):
        """Clear conversation memory and history."""
        self.memory = []
        self.conversation_handler.clear_history()
        logger.info("Jarvis memory and conversation history cleared")
        if self.conversation_chain and hasattr(self.conversation_chain, 'memory'):
            self.conversation_chain.memory.clear()
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
            'memory_size': len(self.memory),
            'temperature': self.temperature,
            'max_length': self.max_length,
            'status': 'operational' if self.model else 'limited',
            'features': [
                'Advanced Web Search & Scraping',
                'Real-time Data Gathering',
                'Grammar Correction',
                'Interactive Quizzes',
                'Knowledge Base',
                'Feedback System',
                'Intelligent API Routing',
                'Personal AI for Heoster'
            ]
        }
