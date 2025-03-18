import json
import logging
import asyncio

from confluent_kafka import Consumer, KafkaException, KafkaError
from concurrent.futures import ThreadPoolExecutor

from src.repositories.event import EventRepository
from src.service.processing_service import processing


logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


class KafkaConsumerBase:
    def __init__(self, config, topics):
        """
        Инициализирует Kafka-консьюмер.

        :param config: Конфигурация консьюмера (словарь).
        :param topics: Список топиков для подписки.
        """
        self.config = config
        self.topics = topics
        self.consumer = None
        self.event_repository = EventRepository()

        try:
            self.consumer = Consumer(self.config)
            logging.info("Консьюмер успешно создан.")
        except Exception as e:
            logging.error(f"Ошибка при создании консьюмера: {e}")
            raise

    def subscribe_to_topics(self):
        """
        Подписывает консьюмер на указанные топики.
        """
        if not self.consumer:
            raise RuntimeError("Консьюмер не создан.")
        try:
            self.consumer.subscribe(self.topics)
            logging.info(f"Подписан на топики: {self.topics}")
        except KafkaException as e:
            logging.error(f"Ошибка подписки на топики: {e}")
            raise RuntimeError(f"Не удалось подписаться на топики: {str(e)}")

    async def process_message(self, msg):
        """
        Обрабатывает полученное сообщение.

        :param msg: Сообщение из Kafka.
        """
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logging.warning(
                    f"Достигнут конец партиции: {msg.topic()} [{msg.partition()}]"
                )
            elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                logging.error(f"Топик не существует: {msg.topic()}")
            else:
                logging.error(
                    f"Ошибка Kafka в топике {msg.topic()} [{msg.partition()}]: "
                    f"{msg.error().str()} (код: {msg.error().code()})"
                )
        else:
            try:
                message_value = msg.value().decode("utf-8")
                message_data = json.loads(message_value)
                logging.info(f"Обработка сообщения из {msg.topic()}: {message_data}")
                await processing(message_data)
            except json.JSONDecodeError:
                logging.error(f"Получено не-JSON сообщение: {message_value}")

    def poll_message(self, consumer, timeout=1.0):
        if not consumer:
            raise RuntimeError("Консьюмер не инициализирован.")
        return consumer.poll(timeout)

    async def run_consumer(self):
        loop = asyncio.get_running_loop()
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                while True:
                    try:
                        message = await loop.run_in_executor(
                            pool, self.poll_message, self.consumer
                        )
                        if message:
                            await self.process_message(message)
                        await asyncio.sleep(0.01)
                    except Exception as e:
                        logging.error(f"Ошибка в цикле обработки: {e}")
        except KeyboardInterrupt:
            logging.info("Прервано пользователем.")
        finally:
            self.close()

    def close(self):
        """
        Корректно закрывает консьюмер.
        """
        if self.consumer:
            self.consumer.close()
            logging.info("Консьюмер закрыт.")
