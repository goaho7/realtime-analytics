import asyncio
import logging
import sys
import sentry_sdk

from settings.config import settings
from src.service.kafka_consumer import KafkaConsumerBase


KAFKA_CONFIG = {
    "bootstrap.servers": "broker:29092",
    "group.id": "event-consumer-group",
    "auto.offset.reset": "latest",
}


async def main():
    consumer = KafkaConsumerBase(config=KAFKA_CONFIG, topics=["sensor-events"])
    consumer.subscribe_to_topics()
    await consumer.run_consumer()


if __name__ == "__main__":
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0,
        )
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)
