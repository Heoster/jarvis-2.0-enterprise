#!/usr/bin/env python3
"""
JARVIS MASTER - Complete AI Assistant with ALL Features Working
Unified intelligent brain combining all capabilities into one powerful system
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Core imports
from core.logger import get_logger, setup_logging
from core.jarvis_brain import JarvisBrain
from core.web_scraper import get_web_scraper
from core.indian_apis import get_indian_api
from core.realtime_data import RealTimeDataManager
from core.api_router import get_api_router
from core.config import get_config

logger = get_logger(__name__)


class JarvisMaster:
    """
    Master Jarvis - Complete AI Assistant
    
    Features:
    - Advanced Web Search & Scraping (DuckDuckGo + BeautifulSoup)
    - Real-time Data (Weather, News, Wikipedia)
    - Indian APIs (Finance INR, Railway, Mutual Funds, Entertainment)
    - Transformers + LangChain for intelligent responses
    - Natural Language Understanding
    - Contextual Memory & Learning
    - API Routing (Grammar, Quiz, Feedback)
    - Math Execution
    - Multi-modal capabilities
    """
    
    def __init__(self):
        """Initialize Master Jarvis with all systems"""
        logger.info("="*80)
        logger.info("JARVIS MASTER - Initializing Complete AI System")
        logger.info("="*80)
        
        # Get configuration
        self.config = get_config()
        
        # Initialize core brain (Transformers + LangChain)
        logger.info("🧠 Loading Jarvis Brain (Transformers + LangChain)...")
        self.brain = JarvisBrain()
        
        # Initialize real-time data manager
        logger.info("🌐 Initializing Real-time Data Manager...")
        self.realtime_data = RealTimeDataManager(
            weather_api_key=self.config.apis.weather.api_key,
            news_api_key=self.config.apis.news.api_key
        )
        
        # Web scraper and Indian APIs will be initialized async
        self.web_scraper = None
        self.indian_api = None
        self.api_router = None
        
        # Session management
        self.session_id = None
        self.interaction_count = 0
        
        logger.info("✅ JARVIS MASTER initialized successfully")
        logger.info("="*80)
    
    async def initialize_async_components(self):
        """Initialize async components"""
        if self.web_scraper is None:
            logger.info("🔍 Initializing Web Scraper...")
            self.web_scraper = await get_web_scraper()
        
        if self.indian_api is None:
            logger.info("🇮🇳 Initializing Indian APIs...")
            self.indian_api = await get_indian_api()
        
        if self.api_router is None:
            logger.info("🔀 Initializing API Router...")
            self.api_router = get_api_router()
    
    async def process_query(self, query: str) -> str:
        """
        Process user query with full intelligence
        
        Args:
            query: User input
        
        Returns:
            Intelligent response
        """
        try:
            # Ensure async components are initialized
            await self.initialize_async_components()
            
            self.interaction_count += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing Query #{self.interaction_count}: {query[:50]}...")
            logger.info(f"{'='*80}")
            
            # Build comprehensive context
            context = await self._build_context(query)
            
            # Generate response using Jarvis Brain
            # The brain handles:
            # - Web search & scraping
            # - API routing
            # - Indian APIs
            # - Real-time data
            # - Transformers + LangChain
            # - Natural language understanding
            response = await self.brain.generate_response(query, context)
            
            logger.info(f"✅ Response generated successfully")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def _build_context(self, query: str) -> Dict[str, Any]:
        """Build comprehensive context for query processing"""
        context = {
            'session_id': self.session_id or 'default',
            'interaction_count': self.interaction_count,
            'timestamp': datetime.now().isoformat()
        }
        
        # Detect if query needs specific data
        query_lower = query.lower()
        
        # Check for math queries
        if any(word in query_lower for word in ['calculate', 'compute', 'solve', '+', '-', '*', '/']):
            # Math will be handled by execution engine
            context['needs_math'] = True
        
        # Check for weather queries
        if 'weather' in query_lower:
            try:
                location = self._extract_location(query) or "India"
                weather_data = await self.realtime_data.get_weather(location)
                context['realtime_data'] = {'weather': weather_data}
            except Exception as e:
                logger.warning(f"Weather fetch failed: {e}")
        
        # Check for news queries
        if 'news' in query_lower:
            try:
                news_data = await self.realtime_data.get_news(limit=5)
                if 'realtime_data' not in context:
                    context['realtime_data'] = {}
                context['realtime_data']['news'] = news_data
            except Exception as e:
                logger.warning(f"News fetch failed: {e}")
        
        # Check for knowledge queries
        if any(word in query_lower for word in ['what is', 'who is', 'tell me about']):
            try:
                topic = self._extract_topic(query)
                if topic:
                    knowledge_data = await self.realtime_data.get_knowledge(topic)
                    if 'realtime_data' not in context:
                        context['realtime_data'] = {}
                    context['realtime_data']['knowledge'] = knowledge_data
            except Exception as e:
                logger.warning(f"Knowledge fetch failed: {e}")
        
        return context
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        # Simple extraction - can be enhanced
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ['in', 'at', 'for']:
                if i + 1 < len(words):
                    return ' '.join(words[i+1:i+3])
        return None
    
    def _extract_topic(self, query: str) -> Optional[str]:
        """Extract topic from query"""
        query_lower = query.lower()
        for phrase in ['what is', 'who is', 'tell me about', 'information on']:
            if phrase in query_lower:
                topic = query_lower.split(phrase)[-1].strip()
                # Remove question marks and clean up
                topic = topic.replace('?', '').strip()
                return topic
        return None
    
    async def start_session(self, session_id: Optional[str] = None):
        """Start a new session"""
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.interaction_count = 0
        logger.info(f"📝 Session started: {self.session_id}")
    
    async def get_greeting(self) -> str:
        """Get personalized greeting"""
        return await self.brain.generate_greeting()
    
    async def get_farewell(self) -> str:
        """Get personalized farewell"""
        return await self.brain.generate_farewell()
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        brain_status = self.brain.get_status()
        
        return {
            'system': 'JARVIS MASTER',
            'status': 'operational',
            'session_id': self.session_id,
            'interactions': self.interaction_count,
            'brain': brain_status,
            'features': {
                'web_scraping': self.web_scraper is not None,
                'indian_apis': self.indian_api is not None,
                'api_routing': self.api_router is not None,
                'realtime_data': True,
                'transformers': brain_status.get('transformer_loaded', False),
                'langchain': brain_status.get('langchain_enabled', False)
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown"""
        logger.info("Shutting down JARVIS MASTER...")
        
        if self.web_scraper:
            await self.web_scraper.close()
        
        if self.indian_api:
            await self.indian_api.close()
        
        logger.info("✅ Shutdown complete")


async def interactive_mode():
    """Run Jarvis in interactive mode"""
    print("\n" + "="*80)
    print("🤖 JARVIS MASTER - Complete AI Assistant")
    print("="*80)
    print("\nInitializing all systems...")
    print()
    
    # Initialize Jarvis Master
    jarvis = JarvisMaster()
    await jarvis.initialize_async_components()
    
    # Start session
    await jarvis.start_session()
    
    # Get greeting
    greeting = await jarvis.get_greeting()
    print(f"\n{greeting}\n")
    
    # Show status
    status = jarvis.get_status()
    print("✅ System Status: OPERATIONAL")
    print()
    print("📦 Available Features:")
    print("  • Advanced Web Search & Scraping (DuckDuckGo)")
    print("  • Real-time Data (Weather, News, Wikipedia)")
    print("  • Indian APIs (Finance INR, Railway, Mutual Funds)")
    print("  • Entertainment (Jokes, Quotes, Images)")
    print("  • Transformers + LangChain AI")
    print("  • Natural Language Understanding")
    print("  • Contextual Memory & Learning")
    print("  • API Routing (Grammar, Quiz, Feedback)")
    print("  • Mathematical Computation")
    print()
    print("Type 'exit', 'quit', or 'bye' to stop")
    print("="*80)
    print()
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                farewell = await jarvis.get_farewell()
                print(f"\n{farewell}\n")
                break
            
            # Check for status command
            if user_input.lower() in ['status', 'info', 'help']:
                status = jarvis.get_status()
                print(f"\n📊 System Status:")
                print(f"  Session: {status['session_id']}")
                print(f"  Interactions: {status['interactions']}")
                print(f"  Brain: {status['brain']['name']} v{status['brain']['version']}")
                print(f"  Owner: {status['brain']['owner']}")
                print(f"  Developer: {status['brain']['developer']}")
                print()
                continue
            
            # Process query
            print()
            response = await jarvis.process_query(user_input)
            print(f"\nJarvis: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.error(f"Interactive mode error: {e}")
    
    # Shutdown
    await jarvis.shutdown()


async def test_mode():
    """Run Jarvis in test mode"""
    print("\n" + "="*80)
    print("🧪 JARVIS MASTER - Test Mode")
    print("="*80)
    print()
    
    jarvis = JarvisMaster()
    await jarvis.initialize_async_components()
    await jarvis.start_session("test_session")
    
    # Test queries
    test_queries = [
        "Hello Jarvis",
        "What's the weather in Mumbai?",
        "Search for latest AI news",
        "Tell me about Python programming",
        "What's the Bitcoin price in INR?",
        "Tell me a joke",
        "Calculate 25 * 4 + 10",
    ]
    
    print("Running test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_queries)}: {query}")
        print(f"{'='*80}")
        
        response = await jarvis.process_query(query)
        print(f"\nResponse: {response[:200]}...")
        print()
    
    print("\n✅ Test mode complete")
    await jarvis.shutdown()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="JARVIS MASTER - Complete AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode'
    )
    
    args = parser.parse_args()
    
    try:
        if args.test:
            asyncio.run(test_mode())
        else:
            asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
