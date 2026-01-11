from threading import Lock
from typing import Optional

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from app.core.config import settings
from app.logger import logger

_producer_lock = Lock()
_consumer_lock = Lock()

_producer: Optional[AIOKafkaProducer] = None


async def get_producer() -> AIOKafkaProducer:
    global _producer

    if _producer is None:
        with _producer_lock:
            if _producer is None:
                _producer = AIOKafkaProducer(
                    bootstrap_servers=settings.REDPANDA_BOOTSTRAP_SERVERS,
                )
                await _producer.start()
                logger.info("Redpanda producer started")

    return _producer


async def send_message(topic: str, value: bytes, key: bytes | None = None):
    producer = await get_producer()
    await producer.send_and_wait(topic, value=value, key=key)


async def close_producer():
    global _producer

    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("Redpanda producer stopped")
