from threading import Lock
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.logger import logger

_lock = Lock()
_engine = None
_session_factory: Optional[async_sessionmaker] = None

def get_engine():
    global _engine, _session_factory

    if _engine is None:
        with _lock:
            if _engine is None:
                _engine = create_async_engine(
                    settings.POSTGRES_DSN,
                    echo=False,
                    pool_pre_ping=True,
                )

                _session_factory = async_sessionmaker(
                    bind=_engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                )
            
                logger.info("PostgreSQL engine initialized")
    
    return _engine

def get_session_factory()-> async_sessionmaker:
    if _session_factory is None:
        get_engine()
    
    return _session_factory

async def get_db()-> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session