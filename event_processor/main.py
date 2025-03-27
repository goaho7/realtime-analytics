import asyncio
import logging
import sys

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
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)
