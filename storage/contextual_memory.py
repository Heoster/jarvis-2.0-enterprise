"""
Contextual Memory System with LangChain Integration
Implements short-term context and long-term user preferences
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import json
import asyncio

from core.logger import get_logger
from storage.memory_store import MemoryStore

logger = get_logger(__name__)


class ConversationBuffer:
    """Manages short-term conversation context (last N turns)"""
    
    def __init__(self, max_turns: int = 3):
        """
        Initialize conversation buffer.
        
        Args:
            max_turns: Maximum number of conversation turns to keep
        """
        self.max_turns = max_turns
        self.buffer = deque(maxlen=max_turns)
        self.session_start = datetime.utcnow()
    
    def add_turn(self, user_input: str, assistant_response: str, metadata: Optional[Dict] = None):
        """Add a conversation turn to the buffer"""
        turn = {
            'user': user_input,
            'assistant': assistant_response,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        self.buffer.append(turn)
        logger.debug(f"Added turn to buffer. Buffer size: {len(self.buffer)}")
    
    def get_context(self) -> List[Dict[str, Any]]:
        """Get all turns in the buffer"""
        return list(self.buffer)
    
    def get_formatted_context(self) -> str:
        """Get formatted context string for prompt injection"""
        if not self.buffer:
            return ""
        
        context_parts = ["Recent conversation:"]
        for turn in self.buffer:
            context_parts.append(f"User: {turn['user']}")
            context_parts.append(f"Assistant: {turn['assistant']}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()
        self.session_start = datetime.utcnow()
        logger.info("Conversation buffer cleared")
    
    def get_session_duration(self) -> float:
        """Get session duration in seconds"""
        return (datetime.utcnow() - self.session_start).total_seconds()


class UserPreferences:
    """Manages long-term user preferences and learning patterns"""
    
    def __init__(self, memory_store: MemoryStore):
        """
        Initialize user preferences manager.
        
        Args:
            memory_store: Memory store for persistence
        """
        self.memory_store = memory_store
        self.preferences_cache = {}
        self.learning_patterns = {}
    
    async def learn_preference(
        self,
        category: str,
        preference: str,
        value: Any,
        confidence: float = 1.0
    ):
        """
        Learn a user preference.
        
        Args:
            category: Preference category (e.g., 'explanation_style', 'language')
            preference: Specific preference (e.g., 'always_use_examples')
            value: Preference value
            confidence: Confidence score (0-1)
        """
        key = f"pref_{category}_{preference}"
        
        # Store in memory
        await self.memory_store.store_fact(
            key=key,
            value=value,
            source="learned",
            confidence=confidence
        )
        
        # Update cache
        if category not in self.preferences_cache:
            self.preferences_cache[category] = {}
        self.preferences_cache[category][preference] = value
        
        logger.info(f"Learned preference: {category}.{preference} = {value}")
    
    async def get_preference(
        self,
        category: str,
        preference: str,
        default: Any = None
    ) -> Any:
        """
        Get a user preference.
        
        Args:
            category: Preference category
            preference: Specific preference
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        # Check cache first
        if category in self.preferences_cache:
            if preference in self.preferences_cache[category]:
                return self.preferences_cache[category][preference]
        
        # Query from memory store
        key = f"pref_{category}_{preference}"
        facts = await self.memory_store.retrieve_facts(key_pattern=key)
        
        if facts:
            value = facts[0]['value']
            # Update cache
            if category not in self.preferences_cache:
                self.preferences_cache[category] = {}
            self.preferences_cache[category][preference] = value
            return value
        
        return default
    
    async def get_all_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Get all user preferences"""
        facts = await self.memory_store.retrieve_facts(key_pattern="pref_%")
        
        preferences = {}
        for fact in facts:
            # Parse key: pref_category_preference
            parts = fact['key'].split('_', 2)
            if len(parts) >= 3:
                category = parts[1]
                preference = parts[2]
                
                if category not in preferences:
                    preferences[category] = {}
                preferences[category][preference] = fact['value']
        
        return preferences
    
    async def detect_patterns(self, user_input: str, response: str):
        """
        Detect patterns in user interactions to learn preferences.
        
        Args:
            user_input: User's input
            response: Assistant's response
        """
        user_lower = user_input.lower()
        
        # Pattern: User asks for examples
        if any(phrase in user_lower for phrase in ['example', 'show me', 'demonstrate']):
            current = await self.get_preference('explanation_style', 'use_examples', 0)
            await self.learn_preference(
                'explanation_style',
                'use_examples',
                current + 1,
                confidence=0.8
            )
        
        # Pattern: User prefers detailed explanations
        if any(phrase in user_lower for phrase in ['explain', 'detail', 'how does', 'why']):
            current = await self.get_preference('explanation_style', 'detailed', 0)
            await self.learn_preference(
                'explanation_style',
                'detailed',
                current + 1,
                confidence=0.8
            )
        
        # Pattern: User prefers concise answers
        if any(phrase in user_lower for phrase in ['brief', 'short', 'quick', 'tldr']):
            current = await self.get_preference('explanation_style', 'concise', 0)
            await self.learn_preference(
                'explanation_style',
                'concise',
                current + 1,
                confidence=0.8
            )
        
        # Pattern: User prefers step-by-step
        if any(phrase in user_lower for phrase in ['step by step', 'guide', 'tutorial']):
            current = await self.get_preference('explanation_style', 'step_by_step', 0)
            await self.learn_preference(
                'explanation_style',
                'step_by_step',
                current + 1,
                confidence=0.8
            )


class ContextualMemory:
    """
    Main contextual memory system integrating short-term and long-term memory
    """
    
    def __init__(self, memory_store: MemoryStore, max_turns: int = 3):
        """
        Initialize contextual memory system.
        
        Args:
            memory_store: Memory store for persistence
            max_turns: Maximum conversation turns to keep in buffer
        """
        self.memory_store = memory_store
        self.conversation_buffer = ConversationBuffer(max_turns=max_turns)
        self.user_preferences = UserPreferences(memory_store)
        
        # Session tracking
        self.session_id = None
        self.session_metadata = {}
        
        logger.info("Contextual memory system initialized")
    
    def start_session(self, session_id: str, metadata: Optional[Dict] = None):
        """
        Start a new conversation session.
        
        Args:
            session_id: Unique session identifier
            metadata: Session metadata
        """
        self.session_id = session_id
        self.session_metadata = metadata or {}
        self.conversation_buffer.clear()
        logger.info(f"Started new session: {session_id}")
    
    async def add_interaction(
        self,
        user_input: str,
        assistant_response: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add an interaction to memory.
        
        Args:
            user_input: User's input
            assistant_response: Assistant's response
            metadata: Additional metadata
        """
        # Add to short-term buffer
        self.conversation_buffer.add_turn(user_input, assistant_response, metadata)
        
        # Learn from interaction
        await self.user_preferences.detect_patterns(user_input, assistant_response)
        
        # Store in long-term memory
        await self.memory_store.store_conversation(
            self._create_conversation_object(user_input, assistant_response, metadata)
        )
    
    def _create_conversation_object(self, user_input: str, response: str, metadata: Optional[Dict]):
        """Create conversation object for storage"""
        from core.models import Conversation, Intent, Action
        import uuid
        
        # Create minimal objects for storage
        intent = Intent(
            name=metadata.get('intent', 'general') if metadata else 'general',
            confidence=metadata.get('confidence', 1.0) if metadata else 1.0
        )
        
        return Conversation(
            id=str(uuid.uuid4()),
            user_input=user_input,
            assistant_response=response,
            intent=intent,
            actions=[]
        )
    
    async def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Get relevant context for a query.
        
        Args:
            query: User query
            
        Returns:
            Context dictionary with short-term and long-term memory
        """
        # Get short-term context
        recent_turns = self.conversation_buffer.get_context()
        
        # Get relevant preferences
        preferences = await self.user_preferences.get_all_preferences()
        
        # Get relevant long-term memories
        # (Could be enhanced with semantic search)
        history = await self.memory_store.get_conversation_history(limit=5)
        
        context = {
            'recent_conversation': recent_turns,
            'user_preferences': preferences,
            'relevant_history': [
                {
                    'user': conv.user_input,
                    'assistant': conv.assistant_response,
                    'timestamp': conv.timestamp
                }
                for conv in history
            ],
            'session_duration': self.conversation_buffer.get_session_duration(),
            'session_metadata': self.session_metadata
        }
        
        return context
    
    def get_formatted_context(self, include_preferences: bool = True) -> str:
        """
        Get formatted context string for prompt injection.
        
        Args:
            include_preferences: Whether to include user preferences
            
        Returns:
            Formatted context string
        """
        parts = []
        
        # Add recent conversation
        recent = self.conversation_buffer.get_formatted_context()
        if recent:
            parts.append(recent)
        
        # Add preferences if requested
        if include_preferences and self.user_preferences.preferences_cache:
            parts.append("\nUser preferences:")
            for category, prefs in self.user_preferences.preferences_cache.items():
                for pref, value in prefs.items():
                    if isinstance(value, int) and value > 2:
                        parts.append(f"- User prefers {pref.replace('_', ' ')}")
        
        return "\n".join(parts)
    
    async def learn_from_feedback(self, feedback: str, context: Dict[str, Any]):
        """
        Learn from user feedback.
        
        Args:
            feedback: User feedback
            context: Context of the interaction
        """
        feedback_lower = feedback.lower()
        
        # Positive feedback
        if any(word in feedback_lower for word in ['good', 'great', 'perfect', 'thanks', 'helpful']):
            # Reinforce current preferences
            logger.info("Positive feedback received, reinforcing preferences")
        
        # Negative feedback
        elif any(word in feedback_lower for word in ['wrong', 'bad', 'not helpful', 'incorrect']):
            # Adjust preferences
            logger.info("Negative feedback received, adjusting preferences")
        
        # Specific preference feedback
        if 'more examples' in feedback_lower or 'show examples' in feedback_lower:
            await self.user_preferences.learn_preference(
                'explanation_style',
                'always_use_examples',
                True,
                confidence=1.0
            )
        
        if 'simpler' in feedback_lower or 'easier' in feedback_lower:
            await self.user_preferences.learn_preference(
                'explanation_style',
                'simplify',
                True,
                confidence=1.0
            )
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what has been learned about the user"""
        preferences = await self.user_preferences.get_all_preferences()
        
        summary = {
            'total_preferences': sum(len(prefs) for prefs in preferences.values()),
            'categories': list(preferences.keys()),
            'preferences': preferences,
            'session_duration': self.conversation_buffer.get_session_duration(),
            'turns_in_session': len(self.conversation_buffer.buffer)
        }
        
        return summary
    
    def clear_session(self):
        """Clear current session"""
        self.conversation_buffer.clear()
        self.session_id = None
        self.session_metadata = {}
        logger.info("Session cleared")


# Singleton instance
_contextual_memory = None

async def get_contextual_memory(memory_store: Optional[MemoryStore] = None) -> ContextualMemory:
    """Get or create contextual memory instance"""
    global _contextual_memory
    if _contextual_memory is None:
        if memory_store is None:
            memory_store = MemoryStore()
        _contextual_memory = ContextualMemory(memory_store)
    return _contextual_memory
