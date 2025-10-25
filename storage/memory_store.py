"""Memory store for persisting user facts and conversation history."""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import asyncio
from contextlib import asynccontextmanager

from core.models import Conversation
from core.logger import get_logger

logger = get_logger(__name__)


class MemoryStore:
    """SQLite-based memory store with encryption support."""
    
    def __init__(
        self,
        db_path: str = "data/memory.db",
        encryption_key: Optional[bytes] = None,
        enable_wal: bool = True
    ):
        """
        Initialize memory store.
        
        Args:
            db_path: Path to SQLite database file
            encryption_key: Encryption key for sensitive data (32 bytes)
            enable_wal: Enable Write-Ahead Logging for better concurrency
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate a key if none provided (store securely in production!)
            self.cipher = Fernet(Fernet.generate_key())
        
        self.enable_wal = enable_wal
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        if self.enable_wal:
            cursor.execute("PRAGMA journal_mode=WAL")
        
        # User facts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                encrypted BOOLEAN DEFAULT 0,
                source TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(key)
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_input TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                intent TEXT NOT NULL,
                actions TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Activity logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_key ON user_facts(key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_logs(timestamp)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Memory store initialized at {self.db_path}")

    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(data.encode()).decode()
    
    async def store_fact(
        self,
        key: str,
        value: Any,
        source: str = "user",
        confidence: float = 1.0,
        encrypt: bool = False
    ) -> None:
        """
        Store a user fact.
        
        Args:
            key: Fact key/identifier
            value: Fact value (will be JSON serialized)
            source: Source of the fact
            confidence: Confidence score (0-1)
            encrypt: Whether to encrypt the value
        """
        # Serialize value
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        # Encrypt if requested
        if encrypt:
            value_str = self._encrypt(value_str)
        
        # Run in thread pool to avoid blocking
        await asyncio.to_thread(self._store_fact_sync, key, value_str, encrypt, source, confidence)
    
    def _store_fact_sync(
        self,
        key: str,
        value_str: str,
        encrypted: bool,
        source: str,
        confidence: float
    ) -> None:
        """Synchronous fact storage."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_facts (key, value, encrypted, source, confidence)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                encrypted = excluded.encrypted,
                source = excluded.source,
                confidence = excluded.confidence,
                updated_at = CURRENT_TIMESTAMP
        """, (key, value_str, encrypted, source, confidence))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Stored fact: {key}")
    
    async def retrieve_facts(
        self,
        key_pattern: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve user facts.
        
        Args:
            key_pattern: SQL LIKE pattern for key matching (None = all)
            min_confidence: Minimum confidence threshold
            limit: Maximum number of facts to return
            
        Returns:
            List of fact dictionaries
        """
        return await asyncio.to_thread(
            self._retrieve_facts_sync,
            key_pattern,
            min_confidence,
            limit
        )
    
    def _retrieve_facts_sync(
        self,
        key_pattern: Optional[str],
        min_confidence: float,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Synchronous fact retrieval."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if key_pattern:
            cursor.execute("""
                SELECT * FROM user_facts
                WHERE key LIKE ? AND confidence >= ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (key_pattern, min_confidence, limit))
        else:
            cursor.execute("""
                SELECT * FROM user_facts
                WHERE confidence >= ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (min_confidence, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to dictionaries and decrypt if needed
        facts = []
        for row in rows:
            fact = dict(row)
            
            # Decrypt value if encrypted
            if fact['encrypted']:
                try:
                    fact['value'] = self._decrypt(fact['value'])
                except Exception as e:
                    logger.error(f"Failed to decrypt fact {fact['key']}: {e}")
                    continue
            
            # Try to parse JSON value
            try:
                fact['value'] = json.loads(fact['value'])
            except (json.JSONDecodeError, TypeError):
                pass  # Keep as string
            
            facts.append(fact)
        
        return facts

    
    async def store_conversation(self, conversation: Conversation) -> None:
        """
        Store a conversation turn.
        
        Args:
            conversation: Conversation object to store
        """
        await asyncio.to_thread(self._store_conversation_sync, conversation)
    
    def _store_conversation_sync(self, conversation: Conversation) -> None:
        """Synchronous conversation storage."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (id, user_input, assistant_response, intent, actions, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conversation.id,
            conversation.user_input,
            conversation.assistant_response,
            json.dumps(conversation.intent.to_dict()),
            json.dumps([a.to_dict() for a in conversation.actions]),
            conversation.timestamp
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Stored conversation: {conversation.id}")
    
    async def get_conversation_history(
        self,
        limit: int = 10,
        since: Optional[datetime] = None
    ) -> List[Conversation]:
        """
        Retrieve conversation history.
        
        Args:
            limit: Maximum number of conversations to return
            since: Only return conversations after this timestamp
            
        Returns:
            List of Conversation objects
        """
        return await asyncio.to_thread(self._get_conversation_history_sync, limit, since)
    
    def _get_conversation_history_sync(
        self,
        limit: int,
        since: Optional[datetime]
    ) -> List[Conversation]:
        """Synchronous conversation history retrieval."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if since:
            cursor.execute("""
                SELECT * FROM conversations
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (since, limit))
        else:
            cursor.execute("""
                SELECT * FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to Conversation objects
        conversations = []
        for row in rows:
            data = dict(row)
            data['intent'] = json.loads(data['intent'])
            data['actions'] = json.loads(data['actions'])
            
            try:
                conversations.append(Conversation.from_dict(data))
            except Exception as e:
                logger.error(f"Failed to parse conversation {data['id']}: {e}")
        
        return conversations
    
    async def store_activity(
        self,
        activity_type: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Store activity log entry.
        
        Args:
            activity_type: Type of activity (web, app, etc.)
            data: Activity data
        """
        await asyncio.to_thread(self._store_activity_sync, activity_type, data)
    
    def _store_activity_sync(self, activity_type: str, data: Dict[str, Any]) -> None:
        """Synchronous activity storage."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO activity_logs (activity_type, data)
            VALUES (?, ?)
        """, (activity_type, json.dumps(data)))
        
        conn.commit()
        conn.close()
    
    async def get_recent_activity(
        self,
        activity_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent activity logs.
        
        Args:
            activity_type: Filter by activity type (None = all)
            hours: Number of hours to look back
            limit: Maximum number of entries to return
            
        Returns:
            List of activity log entries
        """
        return await asyncio.to_thread(
            self._get_recent_activity_sync,
            activity_type,
            hours,
            limit
        )
    
    def _get_recent_activity_sync(
        self,
        activity_type: Optional[str],
        hours: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Synchronous activity retrieval."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        if activity_type:
            cursor.execute("""
                SELECT * FROM activity_logs
                WHERE activity_type = ? AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (activity_type, since, limit))
        else:
            cursor.execute("""
                SELECT * FROM activity_logs
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (since, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to dictionaries
        activities = []
        for row in rows:
            activity = dict(row)
            activity['data'] = json.loads(activity['data'])
            activities.append(activity)
        
        return activities
    
    async def delete_old_data(self, retention_days: int = 30) -> int:
        """
        Delete data older than retention period.
        
        Args:
            retention_days: Number of days to retain data
            
        Returns:
            Number of records deleted
        """
        return await asyncio.to_thread(self._delete_old_data_sync, retention_days)
    
    def _delete_old_data_sync(self, retention_days: int) -> int:
        """Synchronous old data deletion."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        
        # Delete old conversations
        cursor.execute("DELETE FROM conversations WHERE timestamp < ?", (cutoff,))
        conv_deleted = cursor.rowcount
        
        # Delete old activity logs
        cursor.execute("DELETE FROM activity_logs WHERE timestamp < ?", (cutoff,))
        activity_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        total_deleted = conv_deleted + activity_deleted
        logger.info(f"Deleted {total_deleted} old records (retention: {retention_days} days)")
        
        return total_deleted
    
    def close(self) -> None:
        """Close database connections and cleanup."""
        logger.info("Memory store closed")
