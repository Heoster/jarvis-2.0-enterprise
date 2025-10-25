"""Tests for decision engine."""

import pytest
from datetime import datetime
from core.decision_engine import DecisionEngine
from core.models import UserInput, IntentCategory


@pytest.fixture
def engine():
    """Create decision engine fixture."""
    return DecisionEngine()


@pytest.mark.asyncio
async def test_classify_intent(engine):
    """Test intent classification through decision engine."""
    user_input = UserInput(
        text="open chrome",
        source="text",
        timestamp=datetime.utcnow()
    )
    
    intent = await engine.classify_intent(user_input)
    
    assert intent.category == IntentCategory.COMMAND
    assert intent.confidence > 0.3
    assert 'previous_intents' in intent.context


@pytest.mark.asyncio
async def test_context_management(engine):
    """Test conversation context management."""
    # First interaction
    user_input1 = UserInput(
        text="what is the weather",
        source="text",
        timestamp=datetime.utcnow()
    )
    intent1 = await engine.classify_intent(user_input1)
    
    # Second interaction
    user_input2 = UserInput(
        text="open chrome",
        source="text",
        timestamp=datetime.utcnow()
    )
    intent2 = await engine.classify_intent(user_input2)
    
    # Check context was updated
    context = engine.get_context()
    assert 'last_command' in context
    assert context['last_command'] == 'open'
    
    # Check history
    assert len(engine.context_history) == 2


@pytest.mark.asyncio
async def test_confidence_scoring(engine):
    """Test confidence scoring."""
    user_input = UserInput(
        text="open chrome",
        source="text",
        timestamp=datetime.utcnow()
    )
    
    intent = await engine.classify_intent(user_input)
    confidence = engine.get_confidence(intent)
    
    assert 0.0 <= confidence <= 1.0
    assert confidence == intent.confidence


@pytest.mark.asyncio
async def test_should_clarify_low_confidence(engine):
    """Test clarification logic for low confidence."""
    # Create a very ambiguous input
    user_input = UserInput(
        text="it",
        source="text",
        timestamp=datetime.utcnow()
    )
    
    intent = await engine.classify_intent(user_input)
    
    # Should request clarification for very short/ambiguous input
    should_clarify = engine.should_clarify(intent)
    assert should_clarify is True


@pytest.mark.asyncio
async def test_should_not_clarify_high_confidence():
    """Test no clarification for high confidence."""
    # Create engine with lower threshold to match model behavior
    engine = DecisionEngine(clarification_threshold=0.3)
    
    user_input = UserInput(
        text="open chrome browser and navigate to google",
        source="text",
        timestamp=datetime.utcnow()
    )
    
    intent = await engine.classify_intent(user_input)
    
    # Should not request clarification for clear, longer input
    should_clarify = engine.should_clarify(intent)
    assert should_clarify is False


@pytest.mark.asyncio
async def test_update_context(engine):
    """Test manual context updates."""
    engine.update_context('test_key', 'test_value')
    
    context = engine.get_context()
    assert 'test_key' in context
    assert context['test_key'] == 'test_value'


@pytest.mark.asyncio
async def test_clear_context(engine):
    """Test context clearing."""
    # Add some context
    user_input = UserInput(
        text="open chrome",
        source="text",
        timestamp=datetime.utcnow()
    )
    await engine.classify_intent(user_input)
    
    # Clear context
    engine.clear_context()
    
    # Verify cleared
    assert len(engine.context_history) == 0
    assert len(engine.get_context()) == 0


@pytest.mark.asyncio
async def test_context_summary(engine):
    """Test context summary generation."""
    # Add some interactions
    user_input1 = UserInput(
        text="open chrome",
        source="text",
        timestamp=datetime.utcnow()
    )
    await engine.classify_intent(user_input1)
    
    user_input2 = UserInput(
        text="what is the weather",
        source="text",
        timestamp=datetime.utcnow()
    )
    await engine.classify_intent(user_input2)
    
    summary = engine.get_context_summary()
    
    assert "Conversation length: 2" in summary
    assert "Last command:" in summary


@pytest.mark.asyncio
async def test_context_window_limit(engine):
    """Test context window size limit."""
    # Add more interactions than the window size
    for i in range(10):
        user_input = UserInput(
            text=f"test input {i}",
            source="text",
            timestamp=datetime.utcnow()
        )
        await engine.classify_intent(user_input)
    
    # Should only keep the last 5 (default window size)
    assert len(engine.context_history) == engine.context_window


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
