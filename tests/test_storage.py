"""Tests for storage layer components."""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import numpy as np

from storage.memory_store import MemoryStore
from storage.vector_db import VectorDB
from storage.knowledge_cache import KnowledgeCache
from core.models import Conversation, Intent, IntentCategory, Action, ActionType, Document


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.mark.asyncio
async def test_memory_store_facts(temp_dir):
    """Test storing and retrieving facts."""
    db_path = Path(temp_dir) / "memory.db"
    store = MemoryStore(db_path=str(db_path))
    
    # Store a fact
    await store.store_fact("user_name", "Alice", source="user", confidence=1.0)
    
    # Retrieve facts
    facts = await store.retrieve_facts(key_pattern="user_%")
    assert len(facts) == 1
    assert facts[0]['key'] == "user_name"
    assert facts[0]['value'] == "Alice"
    
    store.close()


@pytest.mark.asyncio
async def test_memory_store_conversations(temp_dir):
    """Test storing and retrieving conversations."""
    db_path = Path(temp_dir) / "memory.db"
    store = MemoryStore(db_path=str(db_path))
    
    # Create a conversation
    intent = Intent(IntentCategory.QUESTION, 0.9)
    actions = [Action("a1", ActionType.CALL_API, {}, 0.5, 1)]
    conv = Conversation(
        id="conv_1",
        user_input="What's the weather?",
        assistant_response="It's sunny",
        intent=intent,
        actions=actions
    )
    
    # Store conversation
    await store.store_conversation(conv)
    
    # Retrieve conversations
    history = await store.get_conversation_history(limit=10)
    assert len(history) == 1
    assert history[0].id == "conv_1"
    assert history[0].user_input == "What's the weather?"
    
    store.close()


@pytest.mark.asyncio
async def test_memory_store_encryption(temp_dir):
    """Test encrypted fact storage."""
    db_path = Path(temp_dir) / "memory.db"
    store = MemoryStore(db_path=str(db_path))
    
    # Store encrypted fact
    await store.store_fact("password", "secret123", encrypt=True)
    
    # Retrieve and verify decryption
    facts = await store.retrieve_facts(key_pattern="password")
    assert len(facts) == 1
    assert facts[0]['value'] == "secret123"
    
    store.close()


def test_vector_db_add_search(temp_dir):
    """Test adding and searching vectors."""
    index_path = Path(temp_dir) / "vectors.index"
    metadata_path = Path(temp_dir) / "vectors_metadata.pkl"
    
    db = VectorDB(
        dimension=128,
        index_path=str(index_path),
        metadata_path=str(metadata_path)
    )
    
    # Add some vectors
    embeddings = np.random.rand(5, 128).astype('float32')
    
    asyncio.run(db.add("doc1", embeddings[0], {"text": "Document 1"}))
    asyncio.run(db.add("doc2", embeddings[1], {"text": "Document 2"}))
    asyncio.run(db.add("doc3", embeddings[2], {"text": "Document 3"}))
    
    # Search
    query = embeddings[0]  # Should find doc1 as most similar
    results = asyncio.run(db.search(query, k=3))
    
    assert len(results) == 3
    assert results[0][0] == "doc1"  # Most similar should be doc1
    assert results[0][1] > 0.9  # High similarity score
    
    db.close()


def test_vector_db_batch_operations(temp_dir):
    """Test batch add operations."""
    index_path = Path(temp_dir) / "vectors.index"
    metadata_path = Path(temp_dir) / "vectors_metadata.pkl"
    
    db = VectorDB(
        dimension=64,
        index_path=str(index_path),
        metadata_path=str(metadata_path)
    )
    
    # Batch add
    doc_ids = ["doc1", "doc2", "doc3"]
    embeddings = np.random.rand(3, 64).astype('float32')
    metadata_list = [
        {"text": "Doc 1"},
        {"text": "Doc 2"},
        {"text": "Doc 3"}
    ]
    
    asyncio.run(db.add_batch(doc_ids, embeddings, metadata_list))
    
    # Verify
    stats = db.get_stats()
    assert stats['total_documents'] == 3
    
    db.close()


@pytest.mark.asyncio
async def test_knowledge_cache_store_retrieve(temp_dir):
    """Test storing and retrieving documents."""
    db_path = Path(temp_dir) / "cache.db"
    cache = KnowledgeCache(db_path=str(db_path))
    
    # Store a document
    doc = Document(
        id="doc1",
        text="This is a test document",
        source="web",
        metadata={"url": "https://example.com"}
    )
    
    await cache.store_document(doc)
    
    # Retrieve document
    retrieved = await cache.get_document("doc1")
    assert retrieved is not None
    assert retrieved.id == "doc1"
    assert retrieved.text == "This is a test document"
    
    cache.close()


@pytest.mark.asyncio
async def test_knowledge_cache_batch_operations(temp_dir):
    """Test batch document storage."""
    db_path = Path(temp_dir) / "cache.db"
    cache = KnowledgeCache(db_path=str(db_path))
    
    # Create multiple documents
    docs = [
        Document(f"doc{i}", f"Document {i}", "web", {"index": i})
        for i in range(5)
    ]
    
    # Batch store
    await cache.store_documents_batch(docs)
    
    # Verify
    stats = cache.get_stats()
    assert stats['total_documents'] == 5
    
    cache.close()


@pytest.mark.asyncio
async def test_knowledge_cache_search(temp_dir):
    """Test document search."""
    db_path = Path(temp_dir) / "cache.db"
    cache = KnowledgeCache(db_path=str(db_path))
    
    # Store documents with searchable text
    docs = [
        Document("doc1", "Python programming tutorial", "web", {}),
        Document("doc2", "JavaScript web development", "web", {}),
        Document("doc3", "Python data science guide", "web", {})
    ]
    
    await cache.store_documents_batch(docs)
    
    # Search for Python
    results = await cache.search_documents("Python", limit=10)
    assert len(results) == 2
    
    cache.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
