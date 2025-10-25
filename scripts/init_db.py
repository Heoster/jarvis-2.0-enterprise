"""Initialize databases for the assistant."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.memory_store import MemoryStore
from storage.vector_db import VectorDB
from storage.knowledge_cache import KnowledgeCache
from monitoring.consent_manager import ConsentManager


def main():
    """Initialize all databases."""
    print("Initializing databases...")
    
    # Initialize memory store
    print("  - Memory store...")
    memory_store = MemoryStore()
    memory_store.close()
    
    # Initialize vector database
    print("  - Vector database...")
    vector_db = VectorDB()
    vector_db.close()
    
    # Initialize knowledge cache
    print("  - Knowledge cache...")
    knowledge_cache = KnowledgeCache()
    knowledge_cache.close()
    
    # Initialize consent manager
    print("  - Consent manager...")
    consent_manager = ConsentManager()
    
    print("\nDatabases initialized successfully!")
    print("Location: data/")


if __name__ == "__main__":
    main()
