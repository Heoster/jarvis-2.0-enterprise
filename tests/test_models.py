"""Tests for core data models."""

import pytest
from datetime import datetime
import numpy as np

from core.models import (
    UserInput, Entity, Sentiment, NLPResult, Intent, IntentCategory,
    Action, ActionPlan, ActionType, ActionStatus, Document, Response, Conversation
)


def test_user_input_serialization():
    """Test UserInput serialization and deserialization."""
    user_input = UserInput(
        text="Hello, world!",
        source="text",
        metadata={"key": "value"}
    )
    
    # Serialize
    data = user_input.to_dict()
    assert data['text'] == "Hello, world!"
    assert data['source'] == "text"
    assert 'timestamp' in data
    
    # Deserialize
    restored = UserInput.from_dict(data)
    assert restored.text == user_input.text
    assert restored.source == user_input.source


def test_entity_creation():
    """Test Entity creation."""
    entity = Entity(
        text="New York",
        type="GPE",
        start=0,
        end=8,
        confidence=0.95
    )
    
    assert entity.text == "New York"
    assert entity.type == "GPE"
    assert entity.confidence == 0.95
    
    # Test serialization
    data = entity.to_dict()
    restored = Entity.from_dict(data)
    assert restored.text == entity.text


def test_sentiment_creation():
    """Test Sentiment creation."""
    sentiment = Sentiment(
        polarity=0.8,
        subjectivity=0.6,
        label="positive"
    )
    
    assert sentiment.polarity == 0.8
    assert sentiment.label == "positive"


def test_nlp_result_serialization():
    """Test NLPResult serialization."""
    entities = [
        Entity("John", "PERSON", 0, 4, 0.9),
        Entity("New York", "GPE", 15, 23, 0.95)
    ]
    
    sentiment = Sentiment(0.5, 0.3, "neutral")
    
    nlp_result = NLPResult(
        text="John lives in New York",
        language="en",
        entities=entities,
        sentiment=sentiment
    )
    
    # Serialize
    data = nlp_result.to_dict()
    assert data['text'] == "John lives in New York"
    assert len(data['entities']) == 2
    
    # Deserialize
    restored = NLPResult.from_dict(data)
    assert restored.text == nlp_result.text
    assert len(restored.entities) == 2
    assert restored.entities[0].text == "John"


def test_intent_creation():
    """Test Intent creation."""
    intent = Intent(
        category=IntentCategory.QUESTION,
        confidence=0.95,
        parameters={"query": "weather"},
        context={"location": "NYC"}
    )
    
    assert intent.category == IntentCategory.QUESTION
    assert intent.confidence == 0.95
    
    # Test serialization
    data = intent.to_dict()
    assert data['category'] == "question"
    
    restored = Intent.from_dict(data)
    assert restored.category == IntentCategory.QUESTION


def test_action_creation():
    """Test Action creation."""
    action = Action(
        id="action_1",
        type=ActionType.CALL_API,
        parameters={"endpoint": "/weather"},
        estimated_time=0.5,
        priority=1
    )
    
    assert action.id == "action_1"
    assert action.type == ActionType.CALL_API
    assert action.status == ActionStatus.PENDING
    
    # Test serialization
    data = action.to_dict()
    restored = Action.from_dict(data)
    assert restored.id == action.id
    assert restored.type == action.type


def test_action_plan_creation():
    """Test ActionPlan creation."""
    actions = [
        Action("a1", ActionType.RETRIEVE_MEMORY, {}, 0.1, 1),
        Action("a2", ActionType.GENERATE_RESPONSE, {}, 0.3, 2)
    ]
    
    plan = ActionPlan(
        actions=actions,
        dependencies={"a2": ["a1"]},
        estimated_time=0.4
    )
    
    assert len(plan.actions) == 2
    assert "a2" in plan.dependencies
    
    # Test serialization
    data = plan.to_dict()
    restored = ActionPlan.from_dict(data)
    assert len(restored.actions) == 2


def test_document_creation():
    """Test Document creation."""
    doc = Document(
        id="doc_1",
        text="This is a test document",
        source="web",
        metadata={"url": "https://example.com"},
        confidence=0.9
    )
    
    assert doc.id == "doc_1"
    assert doc.source == "web"
    
    # Test serialization without embedding
    data = doc.to_dict(include_embedding=False)
    assert 'embedding' not in data
    
    # Test with embedding
    doc.embedding = np.array([0.1, 0.2, 0.3])
    data = doc.to_dict(include_embedding=True)
    assert 'embedding' in data
    
    # Deserialize
    restored = Document.from_dict(data)
    assert restored.id == doc.id
    assert restored.embedding is not None


def test_response_creation():
    """Test Response creation."""
    docs = [
        Document("d1", "Doc 1", "memory", {}, confidence=0.9),
        Document("d2", "Doc 2", "web", {}, confidence=0.8)
    ]
    
    response = Response(
        text="Here is your answer",
        sources=docs,
        confidence=0.85,
        suggestions=["Try this", "Or that"],
        execution_time=0.5
    )
    
    assert response.text == "Here is your answer"
    assert len(response.sources) == 2
    assert len(response.suggestions) == 2
    
    # Test serialization
    data = response.to_dict()
    restored = Response.from_dict(data)
    assert restored.text == response.text
    assert len(restored.sources) == 2


def test_conversation_creation():
    """Test Conversation creation."""
    intent = Intent(IntentCategory.QUESTION, 0.9)
    actions = [Action("a1", ActionType.CALL_API, {}, 0.5, 1)]
    
    conv = Conversation(
        id="conv_1",
        user_input="What's the weather?",
        assistant_response="It's sunny",
        intent=intent,
        actions=actions
    )
    
    assert conv.id == "conv_1"
    assert conv.user_input == "What's the weather?"
    
    # Test serialization
    data = conv.to_dict()
    restored = Conversation.from_dict(data)
    assert restored.id == conv.id
    assert restored.intent.category == IntentCategory.QUESTION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
