"""Tests for intent classification."""

import pytest
from core.intent_classifier import IntentClassifier
from core.models import IntentCategory


@pytest.fixture
def classifier():
    """Create classifier fixture."""
    return IntentClassifier()


@pytest.mark.asyncio
async def test_command_intent(classifier):
    """Test command classification."""
    intent = await classifier.classify("open chrome")
    assert intent.category == IntentCategory.COMMAND
    assert intent.confidence > 0.3  # Realistic threshold for 6-class problem
    assert 'action' in intent.parameters
    assert intent.parameters['action'] == 'open'


@pytest.mark.asyncio
async def test_question_intent(classifier):
    """Test question classification."""
    intent = await classifier.classify("what is the weather today")
    assert intent.category == IntentCategory.QUESTION
    assert intent.confidence > 0.3
    assert 'question_type' in intent.parameters
    assert intent.parameters['question_type'] == 'what'


@pytest.mark.asyncio
async def test_math_intent(classifier):
    """Test math classification."""
    intent = await classifier.classify("what is 5 plus 3")
    assert intent.category == IntentCategory.MATH
    assert intent.confidence > 0.3
    assert 'numbers' in intent.parameters
    assert len(intent.parameters['numbers']) == 2


@pytest.mark.asyncio
async def test_code_intent(classifier):
    """Test code classification."""
    intent = await classifier.classify("write a python function")
    assert intent.category == IntentCategory.CODE
    assert intent.confidence > 0.3


@pytest.mark.asyncio
async def test_fetch_intent(classifier):
    """Test fetch classification."""
    intent = await classifier.classify("search for python tutorials")
    assert intent.category == IntentCategory.FETCH
    assert intent.confidence > 0.3


@pytest.mark.asyncio
async def test_conversational_intent(classifier):
    """Test conversational classification."""
    intent = await classifier.classify("hello")
    assert intent.category == IntentCategory.CONVERSATIONAL
    assert intent.confidence > 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
