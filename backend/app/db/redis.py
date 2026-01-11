from threading import Lock
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings
from app.logger import logger

_lock = Lock()
_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _client

    if _client is None:
        with _lock:
            if _client is None:
                _client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                )
                logger.info("Redis client initialized")

    return _client


async def close_redis():
    global _client

    if _client:
        await _client.close()
        _client = None
        logger.info("Redis connection closed")
