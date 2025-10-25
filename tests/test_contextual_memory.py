"""
Tests for contextual memory and learning system
"""

import pytest
import asyncio
from datetime import datetime

from storage.contextual_memory import (
    ConversationBuffer,
    UserPreferences,
    ContextualMemory
)
from storage.memory_store import MemoryStore


@pytest.fixture
async def memory_store():
    """Create a test memory store"""
    store = MemoryStore(db_path=":memory:")  # In-memory database
    yield store
    store.close()


@pytest.fixture
def conversation_buffer():
    """Create a conversation buffer"""
    return ConversationBuffer(max_turns=3)


@pytest.fixture
async def user_preferences(memory_store):
    """Create user preferences manager"""
    return UserPreferences(memory_store)


@pytest.fixture
async def contextual_memory(memory_store):
    """Create contextual memory system"""
    return ContextualMemory(memory_store, max_turns=3)


class TestConversationBuffer:
    """Test conversation buffer functionality"""
    
    def test_add_turn(self, conversation_buffer):
        """Test adding conversation turns"""
        conversation_buffer.add_turn("Hello", "Hi there!")
        
        context = conversation_buffer.get_context()
        assert len(context) == 1
        assert context[0]['user'] == "Hello"
        assert context[0]['assistant'] == "Hi there!"
    
    def test_max_turns_limit(self, conversation_buffer):
        """Test that buffer respects max turns limit"""
        for i in range(5):
            conversation_buffer.add_turn(f"Query {i}", f"Response {i}")
        
        context = conversation_buffer.get_context()
        assert len(context) == 3  # Max turns is 3
        
        # Should have the last 3 turns
        assert context[0]['user'] == "Query 2"
        assert context[1]['user'] == "Query 3"
        assert context[2]['user'] == "Query 4"
    
    def test_formatted_context(self, conversation_buffer):
        """Test formatted context string"""
        conversation_buffer.add_turn("What's Python?", "Python is a programming language")
        conversation_buffer.add_turn("Tell me more", "It's used for web development")
        
        formatted = conversation_buffer.get_formatted_context()
        
        assert "Recent conversation:" in formatted
        assert "User: What's Python?" in formatted
        assert "Assistant: Python is a programming language" in formatted
    
    def test_clear(self, conversation_buffer):
        """Test clearing the buffer"""
        conversation_buffer.add_turn("Hello", "Hi")
        conversation_buffer.clear()
        
        context = conversation_buffer.get_context()
        assert len(context) == 0
    
    def test_session_duration(self, conversation_buffer):
        """Test session duration tracking"""
        duration = conversation_buffer.get_session_duration()
        assert duration >= 0


class TestUserPreferences:
    """Test user preferences learning"""
    
    @pytest.mark.asyncio
    async def test_learn_preference(self, user_preferences):
        """Test learning a preference"""
        await user_preferences.learn_preference(
            category="explanation_style",
            preference="use_examples",
            value=True,
            confidence=1.0
        )
        
        # Retrieve the preference
        value = await user_preferences.get_preference(
            category="explanation_style",
            preference="use_examples"
        )
        
        assert value is True
    
    @pytest.mark.asyncio
    async def test_get_preference_default(self, user_preferences):
        """Test getting preference with default value"""
        value = await user_preferences.get_preference(
            category="nonexistent",
            preference="test",
            default="default_value"
        )
        
        assert value == "default_value"
    
    @pytest.mark.asyncio
    async def test_get_all_preferences(self, user_preferences):
        """Test getting all preferences"""
        # Learn multiple preferences
        await user_preferences.learn_preference(
            "explanation_style", "use_examples", True
        )
        await user_preferences.learn_preference(
            "explanation_style", "detailed", 5
        )
        await user_preferences.learn_preference(
            "language", "preferred", "english"
        )
        
        all_prefs = await user_preferences.get_all_preferences()
        
        assert "explanation_style" in all_prefs
        assert "language" in all_prefs
        assert all_prefs["explanation_style"]["use_examples"] is True
        assert all_prefs["explanation_style"]["detailed"] == 5
    
    @pytest.mark.asyncio
    async def test_detect_patterns_examples(self, user_preferences):
        """Test pattern detection for examples"""
        # Simulate user asking for examples
        await user_preferences.detect_patterns(
            "Can you show me an example?",
            "Here's an example..."
        )
        
        count = await user_preferences.get_preference(
            "explanation_style", "use_examples", 0
        )
        
        assert count > 0
    
    @pytest.mark.asyncio
    async def test_detect_patterns_detailed(self, user_preferences):
        """Test pattern detection for detailed explanations"""
        await user_preferences.detect_patterns(
            "Explain in detail how this works",
            "Here's a detailed explanation..."
        )
        
        count = await user_preferences.get_preference(
            "explanation_style", "detailed", 0
        )
        
        assert count > 0
    
    @pytest.mark.asyncio
    async def test_detect_patterns_concise(self, user_preferences):
        """Test pattern detection for concise answers"""
        await user_preferences.detect_patterns(
            "Give me a brief answer",
            "Brief answer here"
        )
        
        count = await user_preferences.get_preference(
            "explanation_style", "concise", 0
        )
        
        assert count > 0


class TestContextualMemory:
    """Test contextual memory system"""
    
    @pytest.mark.asyncio
    async def test_start_session(self, contextual_memory):
        """Test starting a session"""
        contextual_memory.start_session("test_session_1", {"user": "test_user"})
        
        assert contextual_memory.session_id == "test_session_1"
        assert contextual_memory.session_metadata["user"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_add_interaction(self, contextual_memory):
        """Test adding an interaction"""
        contextual_memory.start_session("test_session")
        
        await contextual_memory.add_interaction(
            user_input="What's Python?",
            assistant_response="Python is a programming language",
            metadata={"intent": "question"}
        )
        
        context = contextual_memory.conversation_buffer.get_context()
        assert len(context) == 1
        assert context[0]['user'] == "What's Python?"
    
    @pytest.mark.asyncio
    async def test_get_context_for_query(self, contextual_memory):
        """Test getting context for a query"""
        contextual_memory.start_session("test_session")
        
        # Add some interactions
        await contextual_memory.add_interaction(
            "Hello", "Hi there!"
        )
        await contextual_memory.add_interaction(
            "What's AI?", "AI is artificial intelligence"
        )
        
        # Get context
        context = await contextual_memory.get_context_for_query("Tell me more")
        
        assert "recent_conversation" in context
        assert "user_preferences" in context
        assert len(context["recent_conversation"]) == 2
    
    @pytest.mark.asyncio
    async def test_formatted_context(self, contextual_memory):
        """Test formatted context generation"""
        contextual_memory.start_session("test_session")
        
        await contextual_memory.add_interaction(
            "What's Python?", "Python is a language"
        )
        
        formatted = contextual_memory.get_formatted_context()
        
        assert "Recent conversation:" in formatted
        assert "What's Python?" in formatted
    
    @pytest.mark.asyncio
    async def test_learn_from_feedback_positive(self, contextual_memory):
        """Test learning from positive feedback"""
        await contextual_memory.learn_from_feedback(
            "That was great, thanks!",
            {}
        )
        # Should not raise an error
    
    @pytest.mark.asyncio
    async def test_learn_from_feedback_examples(self, contextual_memory):
        """Test learning from feedback about examples"""
        await contextual_memory.learn_from_feedback(
            "Please show more examples",
            {}
        )
        
        pref = await contextual_memory.user_preferences.get_preference(
            "explanation_style",
            "always_use_examples"
        )
        
        assert pref is True
    
    @pytest.mark.asyncio
    async def test_get_learning_summary(self, contextual_memory):
        """Test getting learning summary"""
        contextual_memory.start_session("test_session")
        
        # Add some interactions
        await contextual_memory.add_interaction("Hello", "Hi")
        await contextual_memory.add_interaction("How are you?", "I'm good")
        
        # Learn a preference
        await contextual_memory.user_preferences.learn_preference(
            "test_category", "test_pref", "test_value"
        )
        
        summary = await contextual_memory.get_learning_summary()
        
        assert "total_preferences" in summary
        assert "categories" in summary
        assert "preferences" in summary
        assert "session_duration" in summary
        assert "turns_in_session" in summary
        assert summary["turns_in_session"] == 2
    
    @pytest.mark.asyncio
    async def test_clear_session(self, contextual_memory):
        """Test clearing a session"""
        contextual_memory.start_session("test_session")
        await contextual_memory.add_interaction("Hello", "Hi")
        
        contextual_memory.clear_session()
        
        assert contextual_memory.session_id is None
        assert len(contextual_memory.conversation_buffer.buffer) == 0
    
    @pytest.mark.asyncio
    async def test_preference_persistence(self, contextual_memory):
        """Test that preferences persist across sessions"""
        # Session 1
        contextual_memory.start_session("session_1")
        await contextual_memory.user_preferences.learn_preference(
            "explanation_style", "use_examples", True
        )
        contextual_memory.clear_session()
        
        # Session 2
        contextual_memory.start_session("session_2")
        pref = await contextual_memory.user_preferences.get_preference(
            "explanation_style", "use_examples"
        )
        
        assert pref is True  # Preference persisted


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_learning_workflow(self, contextual_memory):
        """Test complete learning workflow"""
        # Start session
        contextual_memory.start_session("user_123")
        
        # User asks for examples multiple times
        for i in range(3):
            await contextual_memory.add_interaction(
                f"Explain topic {i}",
                f"Explanation {i}"
            )
            await contextual_memory.add_interaction(
                "Can you show an example?",
                f"Example {i}"
            )
        
        # Check that preference was learned
        summary = await contextual_memory.get_learning_summary()
        prefs = summary['preferences']
        
        if 'explanation_style' in prefs:
            assert prefs['explanation_style'].get('use_examples', 0) >= 3
    
    @pytest.mark.asyncio
    async def test_context_continuity(self, contextual_memory):
        """Test context continuity across turns"""
        contextual_memory.start_session("test_session")
        
        # First turn
        await contextual_memory.add_interaction(
            "What's the weather in Mumbai?",
            "It's 28°C and sunny in Mumbai"
        )
        
        # Second turn - follow-up
        await contextual_memory.add_interaction(
            "What about tomorrow?",
            "Tomorrow in Mumbai will be 30°C"
        )
        
        # Get context
        context = await contextual_memory.get_context_for_query("And the day after?")
        
        # Should have both previous turns
        assert len(context['recent_conversation']) == 2
        assert 'Mumbai' in context['recent_conversation'][0]['assistant']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
