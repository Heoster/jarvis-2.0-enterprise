"""
Enhanced Conversation Handler for Natural Language Understanding
Improves Jarvis's ability to understand and respond to normal English
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from core.logger import get_logger

logger = get_logger(__name__)


class ConversationHandler:
    """Handles natural language understanding and contextual responses"""
    
    def __init__(self):
        self.conversation_history = []  # Full conversation history
        self.conversation_context = []  # Recent context (last 10)
        self.last_topic = None
        self.last_query = None
        self.last_response = None
        self.awaiting_clarification = False
        self.clarification_options = []
        self.max_history = 50  # Keep last 50 exchanges
        
        # Common conversational patterns
        self.patterns = {
            'greeting': [
                r'\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b',
                r'\b(what\'s up|wassup|sup)\b'
            ],
            'farewell': [
                r'\b(bye|goodbye|see you|later|farewell)\b',
                r'\b(good\s+night|take care)\b'
            ],
            'thanks': [
                r'\b(thank|thanks|thx|appreciate)\b',
                r'\b(grateful|gratitude)\b'
            ],
            'how_are_you': [
                r'\bhow\s+(are|r)\s+you\b',
                r'\bhow\'s\s+it\s+going\b',
                r'\bhow\s+are\s+things\b'
            ],
            'what_can_you_do': [
                r'\bwhat\s+can\s+you\s+do\b',
                r'\bwhat\s+are\s+you\s+capable\s+of\b',
                r'\bwhat\s+are\s+your\s+(abilities|features|capabilities)\b',
                r'\bhelp\s+me\b'
            ],
            'who_are_you': [
                r'\bwho\s+are\s+you\b',
                r'\bwhat\s+are\s+you\b',
                r'\btell\s+me\s+about\s+yourself\b'
            ],
            'affirmative': [
                r'\b(yes|yeah|yep|sure|okay|ok|alright|correct|right)\b'
            ],
            'negative': [
                r'\b(no|nope|nah|not\s+really|don\'t\s+think\s+so)\b'
            ]
        }
        
        # Response templates
        self.responses = {
            'greeting': [
                "Hello! I'm Jarvis, your personal AI assistant. How may I help you today?",
                "Good day! Jarvis at your service. What can I do for you?",
                "Greetings! I'm here to assist you with anything you need."
            ],
            'farewell': [
                "Goodbye! Feel free to return anytime you need assistance.",
                "Until next time! I'm always here when you need me.",
                "Take care! Don't hesitate to ask if you need anything."
            ],
            'thanks': [
                "You're very welcome! I'm happy to help.",
                "My pleasure! That's what I'm here for.",
                "Glad I could assist you! Let me know if you need anything else."
            ],
            'how_are_you': [
                "I'm functioning optimally, thank you for asking! How can I assist you today?",
                "All systems operational! I'm ready to help you with whatever you need.",
                "I'm doing well, thank you! What can I do for you?"
            ],
            'what_can_you_do': [
                "I can help you with many things! I can:\n"
                "• Search the web and provide detailed information\n"
                "• Check Bitcoin prices and currency rates in INR\n"
                "• Provide Indian Railway train schedules\n"
                "• Show mutual fund NAV information\n"
                "• Tell jokes and show cute animal pictures\n"
                "• Give inspirational quotes\n"
                "• Answer questions and have conversations\n"
                "• Perform calculations\n"
                "• And much more! Just ask me anything.",
                
                "I'm your personal AI assistant with many capabilities:\n"
                "📊 Financial data (crypto, currency rates, mutual funds)\n"
                "🚂 Indian Railway information\n"
                "🔍 Web search and information retrieval\n"
                "😄 Entertainment (jokes, images, quotes)\n"
                "📍 Location and geographical data\n"
                "💬 Natural conversations\n"
                "What would you like help with?"
            ],
            'who_are_you': [
                "I'm Jarvis, an advanced AI assistant created to help you with various tasks. "
                "I can search the web, provide financial information, help with Indian Railway schedules, "
                "entertain you with jokes and quotes, and much more. Think of me as your personal digital assistant!",
                
                "I'm Jarvis - your intelligent AI companion. I'm designed to understand natural language "
                "and assist you with information, entertainment, and various tasks. I specialize in "
                "Indian-specific services like railway information and INR financial data, but I can help "
                "with many other things too!"
            ]
        }
    
    def detect_intent(self, query: str) -> Tuple[Optional[str], float]:
        """
        Detect the intent of a query using pattern matching
        
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        query_lower = query.lower().strip()
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    # Calculate confidence based on pattern match
                    confidence = 0.9 if len(query_lower.split()) <= 5 else 0.7
                    return intent, confidence
        
        return None, 0.0
    
    def get_response(self, intent: str) -> str:
        """Get a response for a detected intent"""
        import random
        
        if intent in self.responses:
            responses = self.responses[intent]
            return random.choice(responses)
        
        return None
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query"""
        entities = {
            'numbers': [],
            'dates': [],
            'locations': [],
            'train_numbers': [],
            'amounts': []
        }
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\b', query)
        entities['numbers'] = numbers
        
        # Extract train numbers (5 digits)
        train_numbers = re.findall(r'\b\d{5}\b', query)
        entities['train_numbers'] = train_numbers
        
        # Extract amounts with currency
        amounts = re.findall(r'₹?\s*\d+(?:,\d{3})*(?:\.\d{2})?', query)
        entities['amounts'] = amounts
        
        # Extract common Indian cities
        indian_cities = ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 
                        'pune', 'ahmedabad', 'jaipur', 'lucknow', 'muzaffarnagar']
        for city in indian_cities:
            if city in query.lower():
                entities['locations'].append(city.title())
        
        return entities
    
    def understand_query(self, query: str) -> Dict[str, Any]:
        """
        Comprehensive query understanding
        
        Returns:
            Dictionary with intent, entities, and context
        """
        intent, confidence = self.detect_intent(query)
        entities = self.extract_entities(query)
        
        # Determine query type
        query_type = self._determine_query_type(query)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'query_type': query_type,
            'original_query': query
        }
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query"""
        query_lower = query.lower()
        
        # Question types
        if query_lower.startswith(('what', 'when', 'where', 'who', 'why', 'how')):
            return 'question'
        
        # Command types
        if query_lower.startswith(('show', 'tell', 'give', 'find', 'search', 'get')):
            return 'command'
        
        # Statement types
        if any(word in query_lower for word in ['is', 'are', 'was', 'were', 'will', 'would']):
            return 'statement'
        
        return 'general'
    
    def generate_contextual_response(self, query: str, understanding: Dict[str, Any]) -> Optional[str]:
        """Generate a contextual response based on understanding"""
        intent = understanding.get('intent')
        
        if intent:
            response = self.get_response(intent)
            if response:
                # Update conversation context
                self.conversation_context.append({
                    'query': query,
                    'intent': intent,
                    'response': response
                })
                return response
        
        return None
    
    def improve_response(self, response: str, query: str) -> str:
        """Improve a response to make it more natural and conversational"""
        # Add conversational elements
        query_lower = query.lower()
        
        # If it's a question, make sure response is informative
        if query_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
            if not any(response.startswith(word) for word in ['The', 'It', 'This', 'That', 'Here']):
                # Add context
                if 'what' in query_lower:
                    response = f"Regarding your question: {response}"
                elif 'how' in query_lower:
                    response = f"Here's how: {response}"
        
        # Add politeness
        if len(response) > 100 and not any(word in response.lower() for word in ['please', 'thank', 'hope']):
            response += " I hope this helps!"
        
        return response
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversation"""
        if not self.conversation_context:
            return "No recent conversation."
        
        recent = self.conversation_context[-3:]
        summary = "Recent conversation:\n"
        for item in recent:
            summary += f"- You asked: {item['query'][:50]}...\n"
        
        return summary


# Singleton instance
_conversation_handler = None

def get_conversation_handler() -> ConversationHandler:
    """Get or create conversation handler instance"""
    global _conversation_handler
    if _conversation_handler is None:
        _conversation_handler = ConversationHandler()
    return _conversation_handler

    
    def add_to_history(self, query: str, response: str, intent: Optional[str] = None):
        """Add exchange to conversation history"""
        exchange = {
            'query': query,
            'response': response,
            'intent': intent,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        self.conversation_history.append(exchange)
        self.last_query = query
        self.last_response = response
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def get_context_for_query(self, query: str) -> str:
        """Build context string from conversation history"""
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-5:]
        context_parts = ["Recent conversation context:"]
        
        for exchange in recent:
            context_parts.append(f"User: {exchange['query']}")
            context_parts.append(f"Jarvis: {exchange['response'][:100]}...")
        
        return "\n".join(context_parts)
    
    def detect_ambiguity(self, query: str, understanding: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Detect if query is ambiguous and needs clarification
        
        Returns:
            Tuple of (is_ambiguous, possible_interpretations)
        """
        query_lower = query.lower()
        possible_meanings = []
        
        # Check for ambiguous terms
        ambiguous_terms = {
            'help': ['technical help', 'information', 'tutorial', 'support'],
            'show': ['display information', 'search for', 'demonstrate'],
            'find': ['search web', 'locate information', 'discover'],
            'check': ['verify', 'look up', 'examine'],
            'get': ['retrieve', 'fetch', 'obtain information']
        }
        
        for term, meanings in ambiguous_terms.items():
            if term in query_lower and len(query.split()) <= 3:
                possible_meanings.extend(meanings)
        
        # Check if query is too vague
        vague_queries = ['something', 'anything', 'stuff', 'things', 'that', 'this', 'it']
        if any(vague in query_lower for vague in vague_queries) and len(query.split()) <= 4:
            return True, ['Please be more specific about what you need']
        
        # Check confidence
        if understanding.get('confidence', 1.0) < 0.3:
            return True, ['I need more information to help you']
        
        # If no clear intent and query is short
        if not understanding.get('intent') and len(query.split()) <= 3:
            return True, ['Could you provide more details?']
        
        return len(possible_meanings) > 0, possible_meanings
    
    def generate_clarification_question(self, query: str, options: List[str]) -> str:
        """Generate a clarification question with options"""
        if not options:
            return "I'm not quite sure what you mean. Could you please provide more details?"
        
        if len(options) == 1:
            return f"I'm not entirely sure what you need. {options[0]}. Could you clarify?"
        
        question = "I want to make sure I understand correctly. Are you looking for:\n"
        for i, option in enumerate(options[:4], 1):  # Limit to 4 options
            question += f"{i}. {option}\n"
        question += "\nPlease let me know which one, or provide more details."
        
        return question
    
    def generate_suggestions(self, query: str) -> List[str]:
        """Generate helpful suggestions based on query"""
        query_lower = query.lower()
        suggestions = []
        
        # Based on keywords, suggest relevant features
        if any(word in query_lower for word in ['price', 'cost', 'money', 'bitcoin', 'crypto']):
            suggestions.append("Check cryptocurrency prices in INR")
            suggestions.append("View currency exchange rates")
        
        if any(word in query_lower for word in ['train', 'railway', 'travel']):
            suggestions.append("Check train schedules from Muzaffarnagar")
            suggestions.append("Get railway information")
        
        if any(word in query_lower for word in ['fund', 'investment', 'nav']):
            suggestions.append("Check mutual fund NAV")
            suggestions.append("Search for specific mutual funds")
        
        if any(word in query_lower for word in ['search', 'find', 'look']):
            suggestions.append("Search the web for information")
            suggestions.append("Find specific topics or articles")
        
        if any(word in query_lower for word in ['joke', 'fun', 'entertain']):
            suggestions.append("Tell you a joke")
            suggestions.append("Show you a cute dog image")
            suggestions.append("Share an inspirational quote")
        
        # If no specific suggestions, provide general ones
        if not suggestions:
            suggestions = [
                "Search for information on the web",
                "Check financial data (crypto, currency, mutual funds)",
                "Get Indian Railway information",
                "Entertainment (jokes, images, quotes)",
                "Answer questions and have conversations"
            ]
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def should_ask_clarification(self, query: str, understanding: Dict[str, Any]) -> bool:
        """Determine if clarification is needed"""
        # Check if awaiting clarification response
        if self.awaiting_clarification:
            return False
        
        # Check for ambiguity
        is_ambiguous, _ = self.detect_ambiguity(query, understanding)
        
        # Check confidence
        low_confidence = understanding.get('confidence', 1.0) < 0.4
        
        # Check if query is too short and vague
        too_vague = len(query.split()) <= 2 and not understanding.get('intent')
        
        return is_ambiguous or low_confidence or too_vague
    
    def handle_clarification_response(self, query: str) -> Optional[str]:
        """Handle user's response to clarification question"""
        if not self.awaiting_clarification:
            return None
        
        query_lower = query.lower()
        
        # Check if user selected an option
        if query_lower in ['1', '2', '3', '4', '5']:
            option_index = int(query_lower) - 1
            if 0 <= option_index < len(self.clarification_options):
                selected = self.clarification_options[option_index]
                self.awaiting_clarification = False
                self.clarification_options = []
                return f"Got it! You want: {selected}. Let me help you with that."
        
        # Check for affirmative/negative responses
        if any(word in query_lower for word in ['yes', 'yeah', 'correct', 'right', 'exactly']):
            self.awaiting_clarification = False
            return "Great! Let me proceed with that."
        
        if any(word in query_lower for word in ['no', 'nope', 'wrong', 'different']):
            self.awaiting_clarification = False
            return "I see. Could you please rephrase what you need?"
        
        # User provided more details
        self.awaiting_clarification = False
        self.clarification_options = []
        return None  # Process as new query
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversation"""
        if not self.conversation_history:
            return "No recent conversation."
        
        recent = self.conversation_history[-3:]
        summary = "Recent conversation:\n"
        for item in recent:
            summary += f"- You: {item['query'][:50]}...\n"
            summary += f"- Jarvis: {item['response'][:50]}...\n"
        
        return summary
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.conversation_context = []
        self.last_query = None
        self.last_response = None
        self.awaiting_clarification = False
        self.clarification_options = []
        logger.info("Conversation history cleared")
