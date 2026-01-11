from threading import Lock
from typing import Optional

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from app.core.config import settings
from app.logger import logger

_lock = Lock()
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    global _client, _db

    if _client is None:
        with _lock:
            if _client is None:
                try:
                    _client = AsyncIOMotorClient(
                        settings.MONGO_DSN,
                        serverSelectionTimeoutMS=5000,
                    )
                    _db = _client[settings.MONGO_DB]
                    logger.info("MongoDB client initialized")
                except Exception:
                    logger.exception("MongoDB connection failed")
                    raise

    return _client


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        get_client()
    return _db


def get_collection(name: str) -> AsyncIOMotorCollection:
    return get_database()[name]
