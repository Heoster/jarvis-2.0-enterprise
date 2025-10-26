"""
Cache Manager for Jarvis AI system.
Implements intelligent caching with TTL and size limits.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable, Tuple
from collections import OrderedDict
import hashlib
import json

from core.logger import get_logger
from core.constants import CacheSettings

logger = get_logger(__name__)


class CacheEntry:
    """Cache entry with metadata"""
    
    def __init__(self, value: Any, ttl: float):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Access the cached value and update metadata"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.created_at


class CacheManager:
    """
    Intelligent cache manager with TTL and LRU eviction.
    Supports async operations and automatic cleanup.
    """
    
    def __init__(
        self,
        max_size: int = CacheSettings.MAX_CACHE_SIZE,
        default_ttl: float = CacheSettings.DEFAULT_TTL,
        cleanup_interval: float = 300.0  # 5 minutes
    ):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default TTL in seconds
            cleanup_interval: Cleanup interval in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        # Use OrderedDict for LRU behavior
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_removals': 0
        }
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
        
        logger.info(f"Cache manager initialized (max_size: {max_size}, default_ttl: {default_ttl}s)")
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = []
        
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            self.stats['expired_removals'] += 1
        
        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired cache entries")
    
    def _generate_key(self, key_data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(key_data, str):
            return key_data
        
        # Create hash for complex objects
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self.cache:
            # OrderedDict maintains insertion order, but we need LRU
            # Find the least recently accessed entry
            lru_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].last_accessed
            )
            del self.cache[lru_key]
            self.stats['evictions'] += 1
            logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        cache_key = self._generate_key(key)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            if entry.is_expired():
                del self.cache[cache_key]
                self.stats['expired_removals'] += 1
                self.stats['misses'] += 1
                return default
            
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            self.stats['hits'] += 1
            
            return entry.access()
        
        self.stats['misses'] += 1
        return default
    
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        cache_key = self._generate_key(key)
        ttl = ttl if ttl is not None else self.default_ttl
        
        # Remove existing entry if present
        if cache_key in self.cache:
            del self.cache[cache_key]
        
        # Evict if at capacity
        while len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Add new entry
        self.cache[cache_key] = CacheEntry(value, ttl)
        
        logger.debug(f"Cached entry: {cache_key} (ttl: {ttl}s)")
    
    async def get_or_fetch(
        self,
        key: Any,
        fetch_func: Callable,
        ttl: Optional[float] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Get from cache or fetch using function.
        
        Args:
            key: Cache key
            fetch_func: Function to fetch data if not cached
            ttl: Time to live for cached result
            *args: Arguments for fetch function
            **kwargs: Keyword arguments for fetch function
            
        Returns:
            Cached or fetched value
        """
        # Try cache first
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Fetch new value
        try:
            if asyncio.iscoroutinefunction(fetch_func):
                value = await fetch_func(*args, **kwargs)
            else:
                value = fetch_func(*args, **kwargs)
            
            # Cache the result
            self.set(key, value, ttl)
            
            return value
            
        except Exception as e:
            logger.error(f"Fetch function failed for key {key}: {e}")
            raise
    
    def delete(self, key: Any) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted
        """
        cache_key = self._generate_key(key)
        
        if cache_key in self.cache:
            del self.cache[cache_key]
            logger.debug(f"Deleted cache entry: {cache_key}")
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cache entries")
    
    def exists(self, key: Any) -> bool:
        """
        Check if key exists in cache (and is not expired).
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is not expired
        """
        cache_key = self._generate_key(key)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            if entry.is_expired():
                del self.cache[cache_key]
                self.stats['expired_removals'] += 1
                return False
            
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Statistics dictionary
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': hit_rate,
            'evictions': self.stats['evictions'],
            'expired_removals': self.stats['expired_removals'],
            'total_requests': total_requests
        }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get detailed cache information.
        
        Returns:
            Cache information dictionary
        """
        entries_info = []
        
        for key, entry in list(self.cache.items())[:10]:  # Show first 10 entries
            entries_info.append({
                'key': key[:50] + '...' if len(key) > 50 else key,
                'age': entry.get_age(),
                'ttl': entry.ttl,
                'access_count': entry.access_count,
                'expired': entry.is_expired()
            })
        
        return {
            'stats': self.get_stats(),
            'entries': entries_info,
            'cleanup_interval': self.cleanup_interval,
            'default_ttl': self.default_ttl
        }
    
    def set_ttl_for_type(self, data_type: str, ttl: float):
        """
        Set default TTL for specific data types.
        
        Args:
            data_type: Type of data
            ttl: TTL in seconds
        """
        # This could be extended to support per-type TTLs
        logger.info(f"TTL for {data_type} set to {ttl}s")
    
    async def shutdown(self):
        """Shutdown cache manager"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Cache manager shutdown complete")


# Global cache manager instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager