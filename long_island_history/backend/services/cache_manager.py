"""
Cache Manager - Caching Layer for External API Responses

Provides caching to reduce API calls and improve response times.
Supports both in-memory and Redis caching.
"""

import logging
import hashlib
import json
from typing import Optional, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for the application."""

    def __init__(self, use_redis: bool = False, redis_url: str = None):
        self.use_redis = use_redis
        self.redis_url = redis_url
        self.redis_client = None

        # In-memory cache (fallback)
        self._cache: dict = {}
        self._cache_times: dict = {}

        # Default TTLs (in seconds)
        self.default_ttl = 3600  # 1 hour
        self.ttls = {
            "parcel": 86400,      # 24 hours - parcel data changes rarely
            "imagery": 604800,    # 7 days - imagery is static
            "newspaper": 86400,   # 24 hours - newspaper results don't change
            "geocode": 2592000,   # 30 days - addresses don't move
            "events": 604800,     # 7 days - historical events are static
            "synthesis": 3600     # 1 hour - AI synthesis may be refined
        }

        if use_redis and redis_url:
            self._init_redis(redis_url)

    def _init_redis(self, redis_url: str):
        """Initialize Redis connection."""
        try:
            import redis.asyncio as redis
            self.redis_client = redis.from_url(redis_url)
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis initialization failed, using in-memory cache: {e}")
            self.use_redis = False

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"li_history:{prefix}:{key_hash}"

    async def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """Get a value from cache."""
        key = self._generate_key(prefix, *args, **kwargs)

        if self.use_redis and self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        # Fallback to in-memory
        if key in self._cache:
            # Check expiration
            if key in self._cache_times:
                if datetime.now() < self._cache_times[key]:
                    return self._cache[key]
                else:
                    # Expired
                    del self._cache[key]
                    del self._cache_times[key]

        return None

    async def set(
        self,
        prefix: str,
        value: Any,
        *args,
        ttl: int = None,
        **kwargs
    ):
        """Set a value in cache."""
        key = self._generate_key(prefix, *args, **kwargs)
        ttl = ttl or self.ttls.get(prefix, self.default_ttl)

        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        # Fallback to in-memory
        self._cache[key] = value
        self._cache_times[key] = datetime.now() + timedelta(seconds=ttl)

        # Limit in-memory cache size
        self._cleanup_memory_cache()

    async def delete(self, prefix: str, *args, **kwargs):
        """Delete a value from cache."""
        key = self._generate_key(prefix, *args, **kwargs)

        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")

        if key in self._cache:
            del self._cache[key]
            if key in self._cache_times:
                del self._cache_times[key]

    async def clear_prefix(self, prefix: str):
        """Clear all cache entries with a given prefix."""
        pattern = f"li_history:{prefix}:*"

        if self.use_redis and self.redis_client:
            try:
                async for key in self.redis_client.scan_iter(match=pattern):
                    await self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")

        # Clear from in-memory
        keys_to_delete = [
            k for k in self._cache.keys()
            if k.startswith(f"li_history:{prefix}:")
        ]
        for key in keys_to_delete:
            del self._cache[key]
            if key in self._cache_times:
                del self._cache_times[key]

    def _cleanup_memory_cache(self, max_size: int = 1000):
        """Clean up in-memory cache if it gets too large."""
        if len(self._cache) > max_size:
            # Remove expired entries first
            now = datetime.now()
            expired = [
                k for k, t in self._cache_times.items()
                if t < now
            ]
            for key in expired:
                del self._cache[key]
                del self._cache_times[key]

            # If still too large, remove oldest entries
            if len(self._cache) > max_size:
                sorted_keys = sorted(
                    self._cache_times.items(),
                    key=lambda x: x[1]
                )
                for key, _ in sorted_keys[:len(self._cache) - max_size]:
                    del self._cache[key]
                    del self._cache_times[key]

    async def close(self):
        """Close cache connections."""
        if self.redis_client:
            await self.redis_client.close()

    async def health_check(self) -> dict:
        """Check cache health."""
        status = {
            "type": "redis" if self.use_redis else "memory",
            "healthy": True
        }

        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.ping()
                status["redis_connected"] = True
            except Exception as e:
                status["redis_connected"] = False
                status["error"] = str(e)

        status["memory_entries"] = len(self._cache)

        return status


# Decorator for caching function results
def cached(prefix: str, ttl: int = None):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # Get cache from self (assumes class has cache attribute)
            cache = getattr(self, 'cache', None) or getattr(self, '_cache', None)

            if cache:
                # Check cache
                result = await cache.get(prefix, *args, **kwargs)
                if result is not None:
                    return result

            # Execute function
            result = await func(self, *args, **kwargs)

            # Store in cache
            if cache and result is not None:
                await cache.set(prefix, result, *args, ttl=ttl, **kwargs)

            return result
        return wrapper
    return decorator
