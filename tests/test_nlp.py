"""Tests for NLP engine."""

import pytest
import asyncio
from core.nlp import NLPEngine


@pytest.fixture
def nlp_engine():
    """Create NLP engine fixture."""
    return NLPEngine()


@pytest.mark.asyncio
async def test_analyze_basic(nlp_engine):
    """Test basic NLP analysis."""
    result = await nlp_engine.analyze("Hello, how are you today?")
    
    assert result.text == "Hello, how are you today?"
    assert result.language == "en"
    assert result.sentiment is not None
    assert isinstance(result.entities, list)


@pytest.mark.asyncio
async def test_entity_extraction(nlp_engine):
    """Test entity extraction."""
    result = await nlp_engine.analyze("Meet me in New York on Friday")
    
    # Should extract location and date entities
    entity_types = [e.type for e in result.entities]
    assert "GPE" in entity_types or "LOC" in entity_types
    assert "DATE" in entity_types


@pytest.mark.asyncio
async def test_sentiment_positive(nlp_engine):
    """Test positive sentiment."""
    result = await nlp_engine.analyze("I love this amazing product!")
    
    assert result.sentiment.label == "positive"
    assert result.sentiment.polarity > 0


@pytest.mark.asyncio
async def test_sentiment_negative(nlp_engine):
    """Test negative sentiment."""
    result = await nlp_engine.analyze("This is terrible and awful")
    
    assert result.sentiment.label == "negative"
    assert result.sentiment.polarity < 0


@pytest.mark.asyncio
async def test_custom_entity_extraction(nlp_engine):
    """Test custom entity extraction (emails, URLs, etc.)."""
    text = "Contact me at test@example.com or visit https://example.com"
    result = await nlp_engine.analyze(text)
    
    entity_types = [e.type for e in result.entities]
    assert "EMAIL" in entity_types
    assert "URL" in entity_types


@pytest.mark.asyncio
async def test_application_entity_extraction(nlp_engine):
    """Test application name extraction."""
    text = "Open Chrome and navigate to Google"
    result = await nlp_engine.analyze(text)
    
    entity_types = [e.type for e in result.entities]
    assert "APPLICATION" in entity_types


@pytest.mark.asyncio
async def test_action_entity_extraction(nlp_engine):
    """Test action verb extraction."""
    text = "Open the file and close the window"
    result = await nlp_engine.analyze(text)
    
    entity_types = [e.type for e in result.entities]
    assert "ACTION" in entity_types


@pytest.mark.asyncio
async def test_command_entity_extraction(nlp_engine):
    """Test command-specific entity extraction."""
    text = "Open Chrome browser"
    entities = nlp_engine.extract_command_entities(text)
    
    assert entities["action"] == "open"
    assert entities["target"] is not None


@pytest.mark.asyncio
async def test_semantic_parsing(nlp_engine):
    """Test semantic parsing."""
    text = "The cat sat on the mat"
    semantics = await nlp_engine.parse_semantics(text)
    
    assert "noun_chunks" in semantics
    assert "verb_phrases" in semantics
    assert "svo_triples" in semantics
    assert len(semantics["noun_chunks"]) > 0


@pytest.mark.asyncio
async def test_entity_confidence_scoring(nlp_engine):
    """Test entity confidence scoring."""
    text = "Apple Inc. is located in Cupertino, California"
    result = await nlp_engine.analyze(text)
    
    # All entities should have confidence scores
    for entity in result.entities:
        assert 0.0 <= entity.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
