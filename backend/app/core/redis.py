import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any
import redis.asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()

_redis_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


def make_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    payload = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"


def cached(prefix: str, ttl: int | None = None) -> Callable:
    """Async cache decorator. Skips cache if Redis is unavailable."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_ttl = ttl or settings.cache_ttl_seconds
            key = make_cache_key(prefix, *args, **kwargs)
            redis = get_redis()
            try:
                cached_value = await redis.get(key)
                if cached_value:
                    return json.loads(cached_value)
                result = await func(*args, **kwargs)
                await redis.setex(key, cache_ttl, json.dumps(result))
                return result
            except Exception:
                # cache miss on any Redis error, never block the request
                return await func(*args, **kwargs)
        return wrapper
    return decorator