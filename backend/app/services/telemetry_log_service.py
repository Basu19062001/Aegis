from typing import Mapping, Any
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongodb import get_collection
from app.core.exception import (
    TelemetryError,
    TelemetryPersistenceError,
    InvalidTelemetryPayload,
)
from app.logger import logger
from app.api.utils.utils import get_current_time

class TelemetryService:
    def __init__(self, collection: AsyncIOMotorCollection | None = None):
        self._collection = collection or get_collection("raw_events")

    async def store_raw_logs(self, payload: Mapping[str, Any]) -> None:
        
        if not payload:
            raise InvalidTelemetryPayload("Telemetry payload cannot be empty")

        document = dict(payload)
        document.setdefault("ingested_at", get_current_time())

        try:
            await self._collection.insert_one(document)
        except Exception as exc:
            logger.exception("MongoDB insert failed")
            raise TelemetryPersistenceError("Failed to persist telemetry") from exc
