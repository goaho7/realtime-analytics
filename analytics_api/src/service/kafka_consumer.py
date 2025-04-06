import json
import logging
import asyncio
import time

from confluent_kafka import Consumer, KafkaException, KafkaError
from concurrent.futures import ThreadPoolExecutor

from src.repositories.analytics import AnalyticsRepository
from src.api.web_socket.ws_analytics import broadcast_analytics


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
        self.analytics_repository = AnalyticsRepository()
        self.executor = ThreadPoolExecutor(max_workers=1)

        try:
            self.consumer = Consumer(self.config)
            logging.info("Консьюмер успешно создан.")
        except Exception as e:
            logging.error(f"Ошибка при создании консьюмера: {e}")
            self.executor.shutdown(wait=True)
            raise

    def subscribe_to_topics(self, max_retries=3, initial_delay=1):
        """
        Подписывает консьюмер на указанные топики.
        """
        if not self.consumer:
            raise RuntimeError("Консьюмер не создан.")
        attempt = 0
        while attempt < max_retries:
            try:
                self.consumer.subscribe(self.topics)
                logging.info(f"Подписан на топики: {self.topics}")
                break
            except KafkaException as e:
                attempt += 1
                delay = initial_delay * (2 ** (attempt - 1))
                logging.error(
                    f"Ошибка подписки на топики (попытка {attempt}/{max_retries}): {e}"
                )
                if attempt == max_retries:
                    logging.critical("Исчерпаны попытки подписки, завершение работы.")
                    raise RuntimeError(
                        f"Не удалось подписаться на топики после {max_retries} попыток: {str(e)}"
                    )
                logging.info(f"Повторная попытка через {delay} секунд...")
                time.sleep(delay)

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
                raise RuntimeError(f"Ошибка: топик {msg.topic()} не найден")
            else:
                logging.error(
                    f"Ошибка Kafka в топике {msg.topic()} [{msg.partition()}]: "
                    f"{msg.error().str()} (код: {msg.error().code()})"
                )
        else:
            try:
                message_value = msg.value().decode("utf-8")
                message_data = json.loads(message_value)
                logging.debug(f"Обработка сообщения из {msg.topic()}: {message_data}")
                data = await self.analytics_repository.get()
                try:
                    await broadcast_analytics(data)
                except Exception as e:
                    logging.error(f"Ошибка при рассылке данных: {e}")
            except json.JSONDecodeError:
                logging.error(f"Получено не-JSON сообщение: {message_value}")

    def poll_message(self, consumer, timeout=1.0):
        if not consumer:
            raise RuntimeError("Консьюмер не инициализирован.")
        return consumer.poll(timeout)

    async def run_consumer(self):
        loop = asyncio.get_running_loop()
        try:
            while True:
                try:
                    message = await loop.run_in_executor(
                        self.executor, self.poll_message, self.consumer
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
        self.executor.shutdown(wait=True)
        logging.info("ThreadPoolExecutor закрыт.")
