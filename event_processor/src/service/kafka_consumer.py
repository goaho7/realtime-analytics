import json
import logging
import sys

from confluent_kafka import Consumer, KafkaException, KafkaError

from src.repositories.event import EventRepository


logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
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

    def create_consumer(self):
        """
        Создаёт и возвращает Kafka-консьюмер.
        """
        try:
            self.consumer = Consumer(self.config)
            logging.info("Консьюмер успешно создан.")
        except Exception as e:
            logging.error(f"Ошибка при создании консьюмера: {e}")
            sys.exit(1)

    def subscribe_to_topics(self):
        """
        Подписывает консьюмер на указанные топики.
        """
        if not self.consumer:
            raise RuntimeError("Консьюмер не создан. Вызовите метод create_consumer() перед подпиской.")

        try:
            self.consumer.subscribe(self.topics)
            logging.info(f"Подписан на топики: {self.topics}")
        except KafkaException as e:
            logging.error(f"Ошибка подписки на топики: {e}")
            sys.exit(1)

    async def process_message(self, msg):
        """
        Обрабатывает полученное сообщение.
        
        :param msg: Сообщение из Kafka.
        """
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logging.warning(f"Достигнут конец партиции: {msg.topic()} [{msg.partition()}]")
            elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                logging.error(f"Топик не существует: {msg.topic()}")
            else:
                logging.error(f"Ошибка Kafka: {msg.error()}")
        else:
            message_value = msg.value().decode('utf-8')
            try:
                message_data = json.loads(message_value)
                await self.event_repository.create(message_data)
            except json.JSONDecodeError:
                logging.info(f"Получено не-JSON сообщение: {message_value}")

    async def consume_messages(self):
        """
        Запускает цикл чтения сообщений из Kafka.
        """
        if not self.consumer:
            raise RuntimeError("Консьюмер не создан. Вызовите метод create_consumer() перед чтением.")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                await self.process_message(msg)
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
