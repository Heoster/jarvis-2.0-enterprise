"""Knowledge cache for storing and retrieving documents."""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import OrderedDict
import asyncio

from core.models import Document
from core.logger import get_logger

logger = get_logger(__name__)


class LRUCache:
    """Simple LRU (Least Recently Used) cache implementation."""
    
    def __init__(self, capacity: int = 1000):
        """
        Initialize LRU cache.
        
        Args:
            capacity: Maximum number of items to cache
        """
        self.cache: OrderedDict = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key not in self.cache:
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache."""
        if key in self.cache:
            # Update and move to end
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        # Evict oldest if over capacity
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear all items from cache."""
        self.cache.clear()


class KnowledgeCache:
    """SQLite-based knowledge cache with LRU eviction."""
    
    def __init__(
        self,
        db_path: str = "data/cache.db",
        enable_wal: bool = True,
        memory_cache_size: int = 1000
    ):
        """
        Initialize knowledge cache.
        
        Args:
            db_path: Path to SQLite database file
            enable_wal: Enable Write-Ahead Logging
            memory_cache_size: Size of in-memory LRU cache
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.enable_wal = enable_wal
        self.memory_cache = LRUCache(capacity=memory_cache_size)
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Enable WAL mode
        if self.enable_wal:
            cursor.execute("PRAGMA journal_mode=WAL")
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                source TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON documents(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON documents(last_accessed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Knowledge cache initialized at {self.db_path}")

    
    async def store_document(self, document: Document) -> None:
        """
        Store a document in the cache.
        
        Args:
            document: Document to store
        """
        await asyncio.to_thread(self._store_document_sync, document)
        
        # Update memory cache
        self.memory_cache.put(document.id, document)
    
    def _store_document_sync(self, document: Document) -> None:
        """Synchronous document storage."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documents (id, text, source, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                text = excluded.text,
                source = excluded.source,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
        """, (
            document.id,
            document.text,
            document.source,
            json.dumps(document.metadata),
            document.timestamp,
            datetime.utcnow()
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Stored document: {document.id}")
    
    async def store_documents_batch(self, documents: List[Document]) -> None:
        """
        Store multiple documents in batch.
        
        Args:
            documents: List of documents to store
        """
        await asyncio.to_thread(self._store_documents_batch_sync, documents)
        
        # Update memory cache
        for doc in documents:
            self.memory_cache.put(doc.id, doc)
    
    def _store_documents_batch_sync(self, documents: List[Document]) -> None:
        """Synchronous batch document storage."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.utcnow()
        
        data = [
            (
                doc.id,
                doc.text,
                doc.source,
                json.dumps(doc.metadata),
                doc.timestamp,
                now
            )
            for doc in documents
        ]
        
        cursor.executemany("""
            INSERT INTO documents (id, text, source, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                text = excluded.text,
                source = excluded.source,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
        """, data)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(documents)} documents in batch")
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document object or None if not found
        """
        # Check memory cache first
        cached = self.memory_cache.get(doc_id)
        if cached:
            return cached
        
        # Fetch from database
        doc = await asyncio.to_thread(self._get_document_sync, doc_id)
        
        # Update memory cache
        if doc:
            self.memory_cache.put(doc_id, doc)
        
        return doc
    
    def _get_document_sync(self, doc_id: str) -> Optional[Document]:
        """Synchronous document retrieval."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM documents WHERE id = ?
        """, (doc_id,))
        
        row = cursor.fetchone()
        
        if row:
            # Update access statistics
            cursor.execute("""
                UPDATE documents
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE id = ?
            """, (datetime.utcnow(), doc_id))
            conn.commit()
        
        conn.close()
        
        if not row:
            return None
        
        # Convert to Document
        return self._row_to_document(row)
    
    def _row_to_document(self, row: sqlite3.Row) -> Document:
        """Convert database row to Document object."""
        return Document(
            id=row['id'],
            text=row['text'],
            source=row['source'],
            metadata=json.loads(row['metadata']),
            timestamp=datetime.fromisoformat(row['created_at']),
            confidence=1.0
        )
    
    async def get_documents_by_source(
        self,
        source: str,
        limit: int = 100
    ) -> List[Document]:
        """
        Retrieve documents by source.
        
        Args:
            source: Source identifier
            limit: Maximum number of documents to return
            
        Returns:
            List of Document objects
        """
        return await asyncio.to_thread(self._get_documents_by_source_sync, source, limit)
    
    def _get_documents_by_source_sync(self, source: str, limit: int) -> List[Document]:
        """Synchronous source-based retrieval."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM documents
            WHERE source = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (source, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_document(row) for row in rows]
    
    async def search_documents(
        self,
        query: str,
        limit: int = 50
    ) -> List[Document]:
        """
        Simple text search in documents.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching Document objects
        """
        return await asyncio.to_thread(self._search_documents_sync, query, limit)
    
    def _search_documents_sync(self, query: str, limit: int) -> List[Document]:
        """Synchronous text search."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple LIKE search (for more advanced search, use FTS5)
        cursor.execute("""
            SELECT * FROM documents
            WHERE text LIKE ?
            ORDER BY last_accessed DESC
            LIMIT ?
        """, (f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_document(row) for row in rows]
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted, False if not found
        """
        result = await asyncio.to_thread(self._delete_document_sync, doc_id)
        
        # Remove from memory cache
        if doc_id in self.memory_cache.cache:
            del self.memory_cache.cache[doc_id]
        
        return result
    
    def _delete_document_sync(self, doc_id: str) -> bool:
        """Synchronous document deletion."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    async def evict_lru(self, keep_count: int = 1000) -> int:
        """
        Evict least recently used documents.
        
        Args:
            keep_count: Number of documents to keep
            
        Returns:
            Number of documents evicted
        """
        return await asyncio.to_thread(self._evict_lru_sync, keep_count)
    
    def _evict_lru_sync(self, keep_count: int) -> int:
        """Synchronous LRU eviction."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM documents")
        total = cursor.fetchone()[0]
        
        if total <= keep_count:
            conn.close()
            return 0
        
        # Delete oldest accessed documents
        to_delete = total - keep_count
        cursor.execute("""
            DELETE FROM documents
            WHERE id IN (
                SELECT id FROM documents
                ORDER BY last_accessed ASC
                LIMIT ?
            )
        """, (to_delete,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        # Clear memory cache
        self.memory_cache.clear()
        
        logger.info(f"Evicted {deleted} LRU documents")
        return deleted
    
    async def delete_old_documents(self, days: int = 30) -> int:
        """
        Delete documents older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of documents deleted
        """
        return await asyncio.to_thread(self._delete_old_documents_sync, days)
    
    def _delete_old_documents_sync(self, days: int) -> int:
        """Synchronous old document deletion."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        cursor.execute("""
            DELETE FROM documents WHERE created_at < ?
        """, (cutoff,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        # Clear memory cache
        self.memory_cache.clear()
        
        logger.info(f"Deleted {deleted} old documents (>{days} days)")
        return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT source) FROM documents")
        sources = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(access_count) FROM documents")
        avg_access = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_documents': total,
            'unique_sources': sources,
            'avg_access_count': avg_access,
            'memory_cache_size': len(self.memory_cache.cache)
        }
    
    def close(self) -> None:
        """Close the cache."""
        self.memory_cache.clear()
        logger.info("Knowledge cache closed")
