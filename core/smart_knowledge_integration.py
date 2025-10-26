"""
Smart Knowledge Integration System
Automatically integrates knowledge from ALL_APIs_GUIDE.md and data files for enhanced JARVIS intelligence.
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

from core.logger import get_logger
from core.knowledge_expander import get_knowledge_expander
from storage.vector_db import VectorDB
from core.cache_manager import get_cache_manager

logger = get_logger(__name__)


class SmartKnowledgeIntegrator:
    """
    Integrates knowledge from multiple sources to enhance JARVIS capabilities
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize knowledge integrator
        
        Args:
            data_directory: Directory containing knowledge files
        """
        self.data_dir = Path(data_directory)
        self.knowledge_expander = get_knowledge_expander()
        self.vector_db = VectorDB()
        self.cache_manager = get_cache_manager()
        
        # Knowledge categories
        self.knowledge_categories = {
            'api_guides': [],
            'technical_docs': [],
            'conversational_patterns': [],
            'iron_man_responses': [],
            'time_date_patterns': [],
            'greeting_variations': []
        }
        
        logger.info("Smart Knowledge Integrator initialized")
    
    async def integrate_all_knowledge(self) -> Dict[str, int]:
        """
        Integrate all available knowledge sources
        
        Returns:
            Dictionary with integration statistics
        """
        stats = {
            'api_knowledge': 0,
            'data_files': 0,
            'conversational_patterns': 0,
            'iron_man_responses': 0,
            'total_entries': 0
        }
        
        try:
            # Integrate API knowledge
            api_stats = await self._integrate_api_knowledge()
            stats['api_knowledge'] = api_stats
            
            # Integrate data files
            data_stats = await self._integrate_data_files()
            stats['data_files'] = data_stats
            
            # Integrate conversational patterns
            conv_stats = await self._integrate_conversational_patterns()
            stats['conversational_patterns'] = conv_stats
            
            # Integrate Iron Man responses
            iron_stats = await self._integrate_iron_man_responses()
            stats['iron_man_responses'] = iron_stats
            
            # Calculate total
            stats['total_entries'] = sum(stats.values()) - stats['total_entries']
            
            logger.info(f"Knowledge integration complete: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Knowledge integration failed: {e}")
            return stats
    
    async def _integrate_api_knowledge(self) -> int:
        """Integrate API knowledge from ALL_APIs_GUIDE.md"""
        try:
            api_guide_path = Path("ALL_APIs_GUIDE.md")
            if not api_guide_path.exists():
                logger.warning("ALL_APIs_GUIDE.md not found")
                return 0
            
            with open(api_guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract API information
            api_entries = self._extract_api_entries(content)
            
            # Add to knowledge base
            count = 0
            for entry in api_entries:
                self.knowledge_expander.add_knowledge(
                    category='api_integration',
                    subcategory=entry['category'],
                    item={
                        'title': entry['title'],
                        'content': entry['content'],
                        'keywords': entry['keywords'],
                        'tags': ['api', 'integration', entry['category']]
                    }
                )
                count += 1
            
            logger.info(f"Integrated {count} API knowledge entries")
            return count
            
        except Exception as e:
            logger.error(f"API knowledge integration failed: {e}")
            return 0
    
    def _extract_api_entries(self, content: str) -> List[Dict[str, Any]]:
        """Extract API entries from ALL_APIs_GUIDE.md content"""
        entries = []
        
        # Financial APIs
        financial_keywords = [
            'bitcoin', 'cryptocurrency', 'btc', 'currency', 'exchange rate',
            'inr', 'rupee', 'mutual fund', 'nav', 'sbi bluechip', 'hdfc'
        ]
        
        entries.append({
            'category': 'financial',
            'title': 'Indian Financial APIs',
            'content': '''
            JARVIS can provide real-time financial information including:
            - Bitcoin prices in INR from CoinDesk API
            - Currency exchange rates with INR as base
            - Indian mutual fund NAV data from MFAPI
            - Popular funds: SBI Bluechip, HDFC Top 100, ICICI Prudential
            
            Usage examples:
            - "what is bitcoin price in INR"
            - "show me currency exchange rates"
            - "search for SBI bluechip fund NAV"
            ''',
            'keywords': financial_keywords
        })
        
        # Railway APIs
        railway_keywords = [
            'train', 'railway', 'pnr', 'irctc', 'muzaffarnagar', 'delhi',
            'nauchandi express', '14511', 'train schedule'
        ]
        
        entries.append({
            'category': 'railway',
            'title': 'Indian Railway Information',
            'content': '''
            JARVIS provides comprehensive railway information:
            - Popular trains from Muzaffarnagar (14511 Nauchandi Express)
            - Train schedules and routes
            - PNR status checking capabilities
            - Station information and timings
            
            Usage examples:
            - "show me train information"
            - "trains from Muzaffarnagar to Delhi"
            - "check train 14511 schedule"
            ''',
            'keywords': railway_keywords
        })
        
        # Entertainment APIs
        entertainment_keywords = [
            'joke', 'funny', 'laugh', 'dog image', 'cat fact', 'quote',
            'inspire', 'motivational', 'programming joke', 'entertainment'
        ]
        
        entries.append({
            'category': 'entertainment',
            'title': 'Entertainment Features',
            'content': '''
            JARVIS can provide entertainment content:
            - Random jokes and programming humor
            - Cute dog images from Dog CEO API
            - Interesting cat facts and trivia
            - Inspirational quotes from famous people
            
            Usage examples:
            - "tell me a joke"
            - "show me a dog image"
            - "give me an inspirational quote"
            ''',
            'keywords': entertainment_keywords
        })
        
        return entries
    
    async def _integrate_data_files(self) -> int:
        """Integrate knowledge from data directory files"""
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} not found")
            return 0
        
        count = 0
        
        # Process JSON files
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Add to knowledge base
                self.knowledge_expander.add_knowledge(
                    category='data_files',
                    subcategory=json_file.stem,
                    item={
                        'title': f"Data from {json_file.name}",
                        'content': json.dumps(data, indent=2),
                        'tags': ['data', 'json', json_file.stem]
                    }
                )
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to process {json_file}: {e}")
        
        # Process text files
        for txt_file in self.data_dir.glob("*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.knowledge_expander.add_knowledge(
                    category='data_files',
                    subcategory=txt_file.stem,
                    item={
                        'title': f"Content from {txt_file.name}",
                        'content': content,
                        'tags': ['data', 'text', txt_file.stem]
                    }
                )
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to process {txt_file}: {e}")
        
        logger.info(f"Integrated {count} data files")
        return count
    
    async def _integrate_conversational_patterns(self) -> int:
        """Integrate conversational patterns for better understanding"""
        patterns = [
            {
                'pattern': 'greeting_variations',
                'examples': [
                    'hello', 'hi', 'hey', 'hellow', 'helo', 'hllo', 'helllo',
                    'good morning', 'good afternoon', 'good evening',
                    'hi jarvis', 'hey jarvis', 'hello jarvis'
                ],
                'response_type': 'greeting',
                'iron_man_style': True
            },
            {
                'pattern': 'time_queries',
                'examples': [
                    'what time is it', 'current time', 'time now', 'what\'s the time',
                    'tell me the time', 'time please', 'what time'
                ],
                'response_type': 'time_info',
                'iron_man_style': True
            },
            {
                'pattern': 'date_queries', 
                'examples': [
                    'what date is it', 'today\'s date', 'current date', 'what day is it',
                    'tell me the date', 'date please', 'what day'
                ],
                'response_type': 'date_info',
                'iron_man_style': True
            },
            {
                'pattern': 'search_queries',
                'examples': [
                    'search for', 'find', 'look up', 'serach', 'seach',
                    'find me', 'look for', 'tell me about', 'what is', 'who is'
                ],
                'response_type': 'web_search',
                'iron_man_style': False
            }
        ]
        
        count = 0
        for pattern in patterns:
            self.knowledge_expander.add_knowledge(
                category='conversational_patterns',
                subcategory=pattern['pattern'],
                item={
                    'title': f"Pattern: {pattern['pattern']}",
                    'content': f"Examples: {', '.join(pattern['examples'])}",
                    'response_type': pattern['response_type'],
                    'iron_man_style': pattern['iron_man_style'],
                    'tags': ['pattern', 'conversational', pattern['response_type']]
                }
            )
            count += 1
        
        logger.info(f"Integrated {count} conversational patterns")
        return count
    
    async def _integrate_iron_man_responses(self) -> int:
        """Integrate Iron Man style responses and personality"""
        iron_man_responses = [
            {
                'context': 'greeting_morning',
                'responses': [
                    "Good morning, Mr. Stark. All systems are operational and ready for your commands.",
                    "Morning, sir. I trust you slept well? How may I assist you today?",
                    "Good morning, Mr. Stark. Your workshop systems are online and awaiting instructions."
                ]
            },
            {
                'context': 'greeting_afternoon',
                'responses': [
                    "Good afternoon, Mr. Stark. How may I be of service?",
                    "Afternoon, sir. I've been running diagnostics - all systems optimal.",
                    "Good afternoon, Mr. Stark. Ready to tackle any challenges you have in mind?"
                ]
            },
            {
                'context': 'greeting_evening',
                'responses': [
                    "Good evening, Mr. Stark. How was your day?",
                    "Evening, sir. Ready for some evening projects?",
                    "Good evening, Mr. Stark. Shall we review today's accomplishments?"
                ]
            },
            {
                'context': 'time_response',
                'responses': [
                    "The current time is {time}, sir.",
                    "It's {time}, Mr. Stark.",
                    "The time is now {time}. Anything else you need, sir?"
                ]
            },
            {
                'context': 'error_handling',
                'responses': [
                    "I'm experiencing some technical difficulties, sir.",
                    "My systems encountered an issue, Mr. Stark.",
                    "There seems to be a glitch in my matrix, sir.",
                    "I'm running diagnostics on this error, Mr. Stark."
                ]
            },
            {
                'context': 'task_completion',
                'responses': [
                    "Task completed, sir. Anything else?",
                    "Done, Mr. Stark. What's next?",
                    "Mission accomplished, sir.",
                    "All finished, Mr. Stark. How else may I assist?"
                ]
            }
        ]
        
        count = 0
        for response_set in iron_man_responses:
            self.knowledge_expander.add_knowledge(
                category='iron_man_personality',
                subcategory=response_set['context'],
                item={
                    'title': f"Iron Man responses: {response_set['context']}",
                    'content': '\n'.join(response_set['responses']),
                    'context': response_set['context'],
                    'tags': ['iron_man', 'personality', 'responses']
                }
            )
            count += 1
        
        logger.info(f"Integrated {count} Iron Man response sets")
        return count
    
    async def get_contextual_knowledge(self, query: str, context: str = 'general') -> List[Dict[str, Any]]:
        """
        Get contextual knowledge for a query
        
        Args:
            query: User query
            context: Context type (greeting, time, search, etc.)
            
        Returns:
            List of relevant knowledge entries
        """
        # Search in knowledge base
        results = self.knowledge_expander.search_knowledge(query)
        
        # Filter by context if specified
        if context != 'general':
            context_results = []
            for result in results:
                if context in result.get('tags', []) or context in result.get('category', ''):
                    context_results.append(result)
            
            if context_results:
                results = context_results
        
        return results[:5]  # Return top 5 results
    
    async def get_iron_man_response_template(self, context: str) -> Optional[str]:
        """
        Get Iron Man response template for specific context
        
        Args:
            context: Response context (greeting_morning, error_handling, etc.)
            
        Returns:
            Random response template or None
        """
        results = self.knowledge_expander.search_knowledge(context, category='iron_man_personality')
        
        if results:
            import random
            response_set = results[0]
            responses = response_set.get('content', '').split('\n')
            return random.choice([r for r in responses if r.strip()])
        
        return None
    
    async def update_knowledge_from_interaction(self, query: str, response: str, feedback: str):
        """
        Update knowledge base from successful interactions
        
        Args:
            query: User query
            response: JARVIS response  
            feedback: User feedback
        """
        if 'positive' in feedback.lower() or any(word in feedback.lower() for word in [
            'good', 'great', 'excellent', 'perfect', 'helpful', 'correct'
        ]):
            # Add successful interaction to knowledge base
            self.knowledge_expander.add_knowledge(
                category='successful_interactions',
                subcategory='learned_responses',
                item={
                    'title': f"Successful response for: {query[:50]}...",
                    'content': f"Query: {query}\nResponse: {response}\nFeedback: {feedback}",
                    'query_pattern': self._extract_query_pattern(query),
                    'tags': ['learned', 'successful', 'positive_feedback']
                }
            )
            
            logger.info(f"Added successful interaction to knowledge base")
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract pattern from query for future matching"""
        # Simple pattern extraction - could be enhanced with NLP
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what', 'who', 'where', 'when', 'why', 'how']):
            return 'question'
        elif any(word in query_lower for word in ['search', 'find', 'look']):
            return 'search'
        elif any(word in query_lower for word in ['time', 'date']):
            return 'time_date'
        elif any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        else:
            return 'general'


# Global instance
_knowledge_integrator = None

def get_knowledge_integrator() -> SmartKnowledgeIntegrator:
    """Get or create knowledge integrator instance"""
    global _knowledge_integrator
    if _knowledge_integrator is None:
        _knowledge_integrator = SmartKnowledgeIntegrator()
    return _knowledge_integrator