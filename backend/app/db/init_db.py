from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.postgres import Base, get_engine
from app.logger import logger

async def init_db():
    engine: AsyncEngine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("PostgreSQL tables created (if not exists)")
