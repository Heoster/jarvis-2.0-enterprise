"""
Enhanced Contextual Memory with LangChain integration, short-term memory (last 3 turns),
and durable student preferences with learning pattern tracking.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class UserPreferences:
    """Tracks and learns user preferences over time."""
    
    def __init__(self, storage_path: str = "data/user_preferences.json"):
        self.storage_path = Path(storage_path)
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict:
        """Load preferences from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'explanation_style': {},
            'difficulty_level': 'medium',
            'preferred_examples': [],
            'learning_pace': 'normal',
            'interaction_patterns': {},
            'topic_interests': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_preferences(self):
        """Save preferences to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.preferences['last_updated'] = datetime.now().isoformat()
        with open(self.storage_path, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    async def learn_preference(self, category: str, preference: str, value: Any, confidence: float = 1.0):
        """Learn a user preference."""
        if category not in self.preferences:
            self.preferences[category] = {}
        
        # Update preference with confidence weighting
        if preference in self.preferences[category]:
            old_value = self.preferences[category][preference]
            if isinstance(old_value, (int, float)) and isinstance(value, (int, float)):
                # Average numeric values
                self.preferences[category][preference] = (old_value + value * confidence) / (1 + confidence)
            else:
                # Replace non-numeric values
                self.preferences[category][preference] = value
        else:
            self.preferences[category][preference] = value
        
        self._save_preferences()
        logger.info(f"Learned preference: {category}.{preference} = {value}")
    
    async def get_preference(self, category: str, preference: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.preferences.get(category, {}).get(preference, default)
    
    async def get_all_preferences(self) -> Dict:
        """Get all preferences."""
        return self.preferences.copy()
    
    async def update_interaction_pattern(self, pattern_type: str, increment: int = 1):
        """Update interaction pattern counter."""
        patterns = self.preferences.get('interaction_patterns', {})
        patterns[pattern_type] = patterns.get(pattern_type, 0) + increment
        self.preferences['interaction_patterns'] = patterns
        self._save_preferences()


class ShortTermMemory:
    """Manages short-term conversation memory (last 3 turns)."""
    
    def __init__(self, max_turns: int = 3):
        self.max_turns = max_turns
        self.turns = []
        self.current_topic = None
        self.topic_continuity_score = 0.0
    
    def add_turn(self, user_input: str, assistant_response: str, metadata: Optional[Dict] = None):
        """Add a conversation turn."""
        turn = {
            'user': user_input,
            'assistant': assistant_response,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.turns.append(turn)
        
        # Keep only last N turns
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
        
        # Update topic tracking
        self._update_topic_tracking(user_input, metadata)
    
    def _update_topic_tracking(self, user_input: str, metadata: Optional[Dict]):
        """Track topic continuity."""
        if metadata and 'intent' in metadata:
            new_topic = metadata['intent']
            
            if self.current_topic == new_topic:
                self.topic_continuity_score = min(self.topic_continuity_score + 0.2, 1.0)
            else:
                self.topic_continuity_score = 0.5
                self.current_topic = new_topic
    
    def get_recent_turns(self, n: Optional[int] = None) -> List[Dict]:
        """Get recent conversation turns."""
        n = n or self.max_turns
        return self.turns[-n:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent context."""
        if not self.turns:
            return "No recent conversation."
        
        summary_parts = []
        for turn in self.turns:
            summary_parts.append(f"User: {turn['user'][:100]}")
            summary_parts.append(f"Assistant: {turn['assistant'][:100]}")
        
        return "\n".join(summary_parts)
    
    def is_topic_continuation(self) -> bool:
        """Check if current conversation is continuing a topic."""
        return self.topic_continuity_score > 0.6
    
    def clear(self):
        """Clear short-term memory."""
        self.turns = []
        self.current_topic = None
        self.topic_continuity_score = 0.0


class LongTermMemory:
    """Manages long-term memory with semantic search."""
    
    def __init__(self, storage_path: str = "data/long_term_memory.json"):
        self.storage_path = Path(storage_path)
        self.memories = self._load_memories()
    
    def _load_memories(self) -> List[Dict]:
        """Load memories from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_memories(self):
        """Save memories to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    async def store_memory(self, memory_type: str, content: str, metadata: Optional[Dict] = None):
        """Store a long-term memory."""
        memory = {
            'type': memory_type,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'access_count': 0,
            'last_accessed': None
        }
        
        self.memories.append(memory)
        
        # Keep only last 1000 memories
        if len(self.memories) > 1000:
            self.memories = self.memories[-1000:]
        
        self._save_memories()
    
    async def retrieve_memories(self, query: str, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Retrieve relevant memories."""
        relevant = []
        
        for memory in reversed(self.memories):  # Most recent first
            if memory_type and memory['type'] != memory_type:
                continue
            
            # Simple keyword matching (could be enhanced with semantic search)
            if any(word.lower() in memory['content'].lower() for word in query.split()):
                memory['access_count'] += 1
                memory['last_accessed'] = datetime.now().isoformat()
                relevant.append(memory)
            
            if len(relevant) >= limit:
                break
        
        self._save_memories()
        return relevant
    
    async def get_learning_history(self, topic: str) -> List[Dict]:
        """Get learning history for a specific topic."""
        return await self.retrieve_memories(topic, memory_type='learning', limit=10)


class EnhancedContextualMemory:
    """
    Enhanced contextual memory system with:
    - Short-term memory (last 3 turns)
    - Long-term memory with semantic search
    - User preference learning
    - LangChain integration
    - Learning pattern tracking
    """
    
    def __init__(self, max_short_term_turns: int = 3):
        self.short_term = ShortTermMemory(max_turns=max_short_term_turns)
        self.long_term = LongTermMemory()
        self.user_preferences = UserPreferences()
        self.langchain_memory = self._initialize_langchain_memory()
        
        # Session tracking
        self.session_id = None
        self.session_start = None
        self.session_metadata = {}
        
        logger.info("Enhanced Contextual Memory initialized")
    
    def _initialize_langchain_memory(self):
        """Initialize LangChain memory components."""
        try:
            from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
            from langchain.memory import CombinedMemory
            
            # Buffer memory for recent turns
            buffer_memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="input",
                output_key="output"
            )
            
            # Summary memory for longer context
            # summary_memory = ConversationSummaryMemory(
            #     memory_key="summary",
            #     return_messages=True
            # )
            
            # Combined memory
            # combined = CombinedMemory(memories=[buffer_memory, summary_memory])
            
            logger.info("LangChain memory initialized")
            return buffer_memory
            
        except ImportError:
            logger.warning("LangChain not available, using basic memory")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize LangChain memory: {e}")
            return None
    
    def start_session(self, session_id: str, metadata: Optional[Dict] = None):
        """Start a new session."""
        self.session_id = session_id
        self.session_start = datetime.now()
        self.session_metadata = metadata or {}
        logger.info(f"Started session: {session_id}")
    
    async def add_interaction(self, user_input: str, assistant_response: str, metadata: Optional[Dict] = None):
        """Add an interaction to memory."""
        # Add to short-term memory
        self.short_term.add_turn(user_input, assistant_response, metadata)
        
        # Add to LangChain memory if available
        if self.langchain_memory:
            try:
                self.langchain_memory.save_context(
                    {"input": user_input},
                    {"output": assistant_response}
                )
            except Exception as e:
                logger.error(f"Failed to save to LangChain memory: {e}")
        
        # Store important interactions in long-term memory
        if metadata and metadata.get('important'):
            await self.long_term.store_memory(
                memory_type='interaction',
                content=f"User: {user_input}\nAssistant: {assistant_response}",
                metadata=metadata
            )
        
        # Learn from interaction patterns
        await self._learn_from_interaction(user_input, assistant_response, metadata)
    
    async def _learn_from_interaction(self, user_input: str, assistant_response: str, metadata: Optional[Dict]):
        """Learn patterns from interactions."""
        if not metadata:
            return
        
        # Learn explanation style preferences
        if 'asked_for_example' in metadata:
            await self.user_preferences.learn_preference(
                'explanation_style', 'use_examples', True, confidence=0.8
            )
        
        if 'asked_for_details' in metadata:
            await self.user_preferences.learn_preference(
                'explanation_style', 'detailed', True, confidence=0.8
            )
        
        if 'asked_for_summary' in metadata:
            await self.user_preferences.learn_preference(
                'explanation_style', 'concise', True, confidence=0.8
            )
        
        # Track topic interests
        if 'intent' in metadata:
            intent = metadata['intent']
            await self.user_preferences.update_interaction_pattern(f"intent_{intent}")
        
        # Learn difficulty preferences
        if metadata.get('too_easy'):
            current_level = await self.user_preferences.get_preference('difficulty_level', 'medium')
            if current_level == 'easy':
                await self.user_preferences.learn_preference('difficulty_level', 'difficulty_level', 'medium')
            elif current_level == 'medium':
                await self.user_preferences.learn_preference('difficulty_level', 'difficulty_level', 'hard')
        
        if metadata.get('too_hard'):
            current_level = await self.user_preferences.get_preference('difficulty_level', 'medium')
            if current_level == 'hard':
                await self.user_preferences.learn_preference('difficulty_level', 'difficulty_level', 'medium')
            elif current_level == 'medium':
                await self.user_preferences.learn_preference('difficulty_level', 'difficulty_level', 'easy')
    
    async def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """Get relevant context for a query."""
        context = {
            'short_term_history': self.short_term.get_recent_turns(),
            'is_topic_continuation': self.short_term.is_topic_continuation(),
            'current_topic': self.short_term.current_topic,
            'user_preferences': await self.user_preferences.get_all_preferences(),
            'session_id': self.session_id,
            'session_duration': (datetime.now() - self.session_start).total_seconds() if self.session_start else 0
        }
        
        # Get relevant long-term memories
        relevant_memories = await self.long_term.retrieve_memories(query, limit=3)
        context['relevant_memories'] = relevant_memories
        
        # Get LangChain memory if available
        if self.langchain_memory:
            try:
                context['langchain_history'] = self.langchain_memory.load_memory_variables({})
            except:
                pass
        
        return context
    
    async def learn_from_feedback(self, feedback: str, context: Dict):
        """Learn from user feedback."""
        feedback_lower = feedback.lower()
        
        # Positive feedback
        if any(word in feedback_lower for word in ['good', 'great', 'perfect', 'helpful', 'clear']):
            # Reinforce current approach
            if context.get('used_examples'):
                await self.user_preferences.learn_preference(
                    'explanation_style', 'use_examples', True, confidence=1.0
                )
        
        # Negative feedback
        elif any(word in feedback_lower for word in ['confusing', 'unclear', 'complicated', 'too much']):
            # Adjust approach
            if context.get('detailed_explanation'):
                await self.user_preferences.learn_preference(
                    'explanation_style', 'concise', True, confidence=0.9
                )
        
        # Store feedback in long-term memory
        await self.long_term.store_memory(
            memory_type='feedback',
            content=feedback,
            metadata=context
        )
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what has been learned about the user."""
        preferences = await self.user_preferences.get_all_preferences()
        
        summary = {
            'total_interactions': len(self.short_term.turns),
            'current_topic': self.short_term.current_topic,
            'topic_continuity': self.short_term.topic_continuity_score,
            'preferences': preferences,
            'session_info': {
                'session_id': self.session_id,
                'duration_seconds': (datetime.now() - self.session_start).total_seconds() if self.session_start else 0
            }
        }
        
        # Add interaction patterns
        patterns = preferences.get('interaction_patterns', {})
        if patterns:
            most_common = max(patterns.items(), key=lambda x: x[1])
            summary['most_common_intent'] = most_common[0]
        
        return summary
    
    def get_formatted_context(self) -> str:
        """Get formatted context for prompt inclusion."""
        return self.short_term.get_context_summary()
    
    def clear_session(self):
        """Clear current session."""
        self.short_term.clear()
        self.session_id = None
        self.session_start = None
        self.session_metadata = {}
        
        if self.langchain_memory:
            try:
                self.langchain_memory.clear()
            except:
                pass
        
        logger.info("Session cleared")
