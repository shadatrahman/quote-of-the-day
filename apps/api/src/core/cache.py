"""Redis cache configuration and management."""

import json
import pickle
from typing import Any, Optional, Union
from redis.asyncio import Redis, ConnectionPool
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with connection pooling and serialization support."""

    def __init__(self):
        """Initialize cache manager."""
        # Parse Redis URL
        redis_url = settings.REDIS_URL

        # Create connection pool
        self.pool = ConnectionPool.from_url(
            redis_url,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30,
        )

        # Create Redis client
        self.redis = Redis(connection_pool=self.pool)

    async def get(
        self,
        key: str,
        default: Any = None,
        deserialize: bool = True
    ) -> Any:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default

            if not deserialize:
                return value

            # Try JSON deserialization first
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Fall back to pickle
                try:
                    return pickle.loads(value)
                except (pickle.PickleError, TypeError):
                    # Return raw value if deserialization fails
                    return value.decode('utf-8') if isinstance(value, bytes) else value

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set value in cache."""
        try:
            if not serialize:
                serialized_value = value
            else:
                # Try JSON serialization first
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    # Fall back to pickle
                    try:
                        serialized_value = pickle.dumps(value)
                    except Exception:
                        # Store as string if serialization fails
                        serialized_value = str(value)

            await self.redis.set(key, serialized_value, ex=ttl)
            return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in cache."""
        try:
            result = await self.redis.incr(key, amount)
            return result
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key."""
        try:
            result = await self.redis.expire(key, ttl)
            return result
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple keys from cache."""
        try:
            values = await self.redis.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        try:
                            result[key] = pickle.loads(value)
                        except (pickle.PickleError, TypeError):
                            result[key] = value.decode('utf-8') if isinstance(value, bytes) else value
                else:
                    result[key] = None
            return result
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {key: None for key in keys}

    async def set_many(self, mapping: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple keys in cache."""
        try:
            pipe = self.redis.pipeline()
            for key, value in mapping.items():
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    try:
                        serialized_value = pickle.dumps(value)
                    except Exception:
                        serialized_value = str(value)

                if ttl:
                    pipe.setex(key, ttl, serialized_value)
                else:
                    pipe.set(key, serialized_value)

            await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                result = await self.redis.delete(*keys)
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0

    async def ping(self) -> bool:
        """Check Redis connection."""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def info(self) -> dict:
        """Get Redis server info."""
        try:
            return await self.redis.info()
        except Exception as e:
            logger.error(f"Redis info error: {e}")
            return {}

    async def close(self):
        """Close Redis connection."""
        try:
            await self.redis.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


# Create global cache manager instance
cache_manager = CacheManager()


# Cache decorator for functions
def cache_result(key_prefix: str, ttl: int = 3600):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache
            cached_result = await cache_manager.get(key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result, ttl)
            return result

        return wrapper
    return decorator