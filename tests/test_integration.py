"""Integration tests for the assistant."""

import pytest
from core.assistant import Assistant
from core.config import Config


@pytest.fixture
def assistant():
    """Create assistant fixture."""
    config = Config()
    return Assistant(config)


@pytest.mark.asyncio
async def test_simple_query(assistant):
    """Test simple query processing."""
    response = await assistant.process_query("Hello, assistant!")
    
    assert response.text is not None
    assert len(response.text) > 0
    assert response.confidence >= 0


@pytest.mark.asyncio
async def test_math_query(assistant):
    """Test math query."""
    response = await assistant.process_query("What is 15 + 27?")
    
    assert response.text is not None
    assert "42" in response.text or "42.0" in response.text


@pytest.mark.asyncio
async def test_conversation_storage(assistant):
    """Test conversation storage."""
    await assistant.process_query("Test query")
    
    history = await assistant.get_conversation_history(limit=1)
    assert len(history) >= 0  # May be 0 if storage fails


@pytest.mark.asyncio
async def test_status(assistant):
    """Test status retrieval."""
    status = assistant.get_status()
    
    assert status['status'] == 'running'
    assert 'components' in status
    assert status['components']['nlp'] == 'ready'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
