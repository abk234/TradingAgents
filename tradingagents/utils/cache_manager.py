import os
"""
Caching layer with Redis backend
"""
import json
import logging
import hashlib
from typing import Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Caching will be disabled. Install with: pip install redis")


class CacheManager:
    """Redis-based caching for expensive operations"""
    
    def __init__(
        self,
        redis_url: str = None,
        default_ttl: int = 3600,
        key_prefix: str = "ta:"
    ):
        """
        Initialize cache manager
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
            key_prefix: Prefix for all cache keys
        """
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.redis = None

        # Get Redis URL from environment if not provided
        if redis_url is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        if not REDIS_AVAILABLE:
            logger.warning("⚠️  Redis not available. Caching disabled.")
            return
        
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            logger.info("✓ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠️  Redis unavailable: {e}. Caching disabled.")
            self.redis = None
    
    def _make_key(self, namespace: str, *args, **kwargs) -> str:
        """Generate cache key from function args"""
        # Create deterministic hash from arguments
        key_data = json.dumps({
            'args': args,
            'kwargs': sorted(kwargs.items())
        }, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{self.key_prefix}{namespace}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.debug(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        if not self.redis:
            return
        
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.debug(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis:
            return
        
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.debug(f"Cache delete error: {e}")
    
    def clear_namespace(self, namespace: str):
        """Clear all keys in a namespace"""
        if not self.redis:
            return
        
        try:
            pattern = f"{self.key_prefix}{namespace}:*"
            count = 0
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
                count += 1
            logger.info(f"Cleared {count} keys from cache namespace: {namespace}")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
    
    def cached(
        self,
        namespace: str,
        ttl: int = None,
        key_func: Optional[Callable] = None
    ):
        """
        Decorator for caching function results
        
        Args:
            namespace: Cache namespace (e.g., 'stock_data', 'analysis')
            ttl: Time-to-live in seconds (None = use default)
            key_func: Custom function to generate cache key from args
        
        Example:
            @cache.cached('stock_data', ttl=3600)
            def get_stock_data(symbol: str, date: str):
                return expensive_api_call(symbol, date)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._make_key(namespace, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache HIT: {func.__name__}")
                    return cached_result
                
                # Cache miss - execute function
                logger.debug(f"Cache MISS: {func.__name__}")
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl)
                
                return result
            
            # Add cache management methods to wrapper
            wrapper.cache_clear = lambda: self.clear_namespace(namespace)
            wrapper.cache_info = lambda: {
                'namespace': namespace,
                'ttl': ttl or self.default_ttl
            }
            
            return wrapper
        return decorator
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis:
            return {'status': 'disabled'}
        
        try:
            info = self.redis.info('stats')
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            
            return {
                'status': 'connected',
                'total_keys': self.redis.dbsize(),
                'hits': hits,
                'misses': misses,
                'hit_rate': hits / max(1, total) if total > 0 else 0.0
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

