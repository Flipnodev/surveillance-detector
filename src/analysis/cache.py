"""
Caching system for performance optimization.

Implements LRU (Least Recently Used) cache with TTL (Time To Live)
for fast lookups while minimizing memory usage.
"""

import logging
import time
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta


class CacheEntry:
    """Represents a cached entry with TTL."""
    
    def __init__(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Initialize cache entry.
        
        Args:
            key: Cache key
            value: Cached value
            ttl_seconds: Time to live in seconds (None = no expiration)
        """
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def access(self):
        """Record access to this entry."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'key': self.key,
            'created_at': self.created_at.isoformat(),
            'ttl_seconds': self.ttl_seconds,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat(),
            'is_expired': self.is_expired(),
        }


class LRUCache:
    """
    Least Recently Used cache with optional TTL.
    
    Features:
    - O(1) get/set operations
    - Automatic eviction of least recently used items
    - Time-to-live (TTL) support
    - Memory-efficient
    - Statistics tracking
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None,
                 logger: logging.Logger = None):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum cache size (default 1000)
            default_ttl: Default TTL in seconds (None = no expiration)
            logger: Logger instance
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.logger = logger or logging.getLogger(__name__)
        
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        self.logger.info(f"LRU cache initialized: max_size={max_size}, "
                        f"default_ttl={default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        entry.access()
        self.hits += 1
        
        return entry.value
    
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (uses default if None)
        """
        # Use default TTL if not specified
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        # If key exists, remove it first
        if key in self.cache:
            del self.cache[key]
        
        # Create and store entry
        entry = CacheEntry(key, value, ttl_seconds)
        self.cache[key] = entry
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        
        # Evict least recently used if at capacity
        if len(self.cache) > self.max_size:
            lru_key, _ = self.cache.popitem(last=False)
            self.evictions += 1
            self.logger.debug(f"Evicted cache entry: {lru_key}")
    
    def contains(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self.cache:
            return False
        
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            return False
        
        return True
    
    def remove(self, key: str) -> bool:
        """
        Remove entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if removed, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        expired_keys = []
        
        # Find expired entries
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self.cache[key]
            removed += 1
        
        if removed > 0:
            self.logger.debug(f"Cleaned up {removed} expired entries")
        
        return removed
    
    def get_statistics(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate memory size (rough estimate)
        memory_bytes = sum(
            len(key) + len(str(entry.value))
            for key, entry in self.cache.items()
        )
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'evictions': self.evictions,
            'memory_kb': memory_bytes / 1024,
        }
    
    def get_info(self) -> str:
        """Get formatted cache info string."""
        stats = self.get_statistics()
        return (f"Cache: {stats['size']}/{stats['max_size']} entries, "
                f"hit_rate={stats['hit_rate']}, "
                f"memory={stats['memory_kb']:.1f}KB")
    
    def __len__(self) -> int:
        """Get cache size."""
        return len(self.cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key in cache."""
        return self.contains(key)
    
    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return f"LRUCache({stats['size']}/{stats['max_size']}, " \
               f"hit_rate={stats['hit_rate']})"


class CacheManager:
    """
    Manager for multiple caches with different purposes.
    
    Manages caches for:
    - Device lookups
    - SSID geolocation
    - Threat scores
    - GPS coordinates
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize cache manager.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Create caches for different purposes
        self.device_cache = LRUCache(max_size=1000, default_ttl=3600, 
                                     logger=logger)  # 1 hour TTL
        self.ssid_cache = LRUCache(max_size=500, default_ttl=3600,
                                   logger=logger)  # 1 hour TTL
        self.threat_cache = LRUCache(max_size=1000, default_ttl=300,
                                     logger=logger)  # 5 min TTL
        self.gps_cache = LRUCache(max_size=2000, default_ttl=600,
                                  logger=logger)  # 10 min TTL
        
        self.logger.info("Cache manager initialized")
    
    def cleanup_all(self) -> int:
        """
        Clean up all caches.
        
        Returns:
            Total entries removed
        """
        total = 0
        total += self.device_cache.cleanup_expired()
        total += self.ssid_cache.cleanup_expired()
        total += self.threat_cache.cleanup_expired()
        total += self.gps_cache.cleanup_expired()
        
        if total > 0:
            self.logger.debug(f"Cleaned up {total} expired cache entries")
        
        return total
    
    def get_statistics(self) -> Dict:
        """Get statistics from all caches."""
        return {
            'device_cache': self.device_cache.get_statistics(),
            'ssid_cache': self.ssid_cache.get_statistics(),
            'threat_cache': self.threat_cache.get_statistics(),
            'gps_cache': self.gps_cache.get_statistics(),
        }
    
    def get_summary(self) -> str:
        """Get formatted summary of all caches."""
        lines = [
            "Cache Summary:",
            f"  Device: {self.device_cache.get_info()}",
            f"  SSID: {self.ssid_cache.get_info()}",
            f"  Threats: {self.threat_cache.get_info()}",
            f"  GPS: {self.gps_cache.get_info()}",
        ]
        return "\n".join(lines)
    
    def clear_all(self):
        """Clear all caches."""
        self.device_cache.clear()
        self.ssid_cache.clear()
        self.threat_cache.clear()
        self.gps_cache.clear()
        self.logger.info("All caches cleared")