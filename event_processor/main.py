import asyncio
import logging
import sys

from confluent_kafka import KafkaException

from src.service.kafka_consumer import KafkaConsumerBase


MAX_RETRIES = 3
RETRY_DELAY = 5
KAFKA_CONFIG = {
    "bootstrap.servers": "broker:29092",
    "group.id": "event-consumer-group",
    "auto.offset.reset": "latest",
}


async def main():
    consumer = KafkaConsumerBase(config=KAFKA_CONFIG, topics=["sensor-events"])
    retry_delay = RETRY_DELAY

    for attempt in range(MAX_RETRIES):
        try:
            consumer.subscribe_to_topics()
            break
        except KafkaException:
            logging.error(
                f"Повторная попытка подписки через {retry_delay} секунд (попытка {attempt + 1}/{MAX_RETRIES})"
            )
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
    else:
        logging.error("Превышено количество попыток подписки. Завершение.")
        sys.exit(1)

    await consumer.run_consumer()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)
