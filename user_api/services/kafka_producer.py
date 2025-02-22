import json
from confluent_kafka import Producer, KafkaException
from fastapi import HTTPException


class KafkaProducerManager:
    def __init__(self, bootstrap_servers: str):
        """
        Инициализирует Kafka Producer.
        :param bootstrap_servers: Адрес Kafka broker'а.
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})

    def send_message(self, topic: str, message: dict):
        """
        Отправляет сообщение в указанный топик Kafka.
        :param topic: Название топика.
        :param message: Сообщение для отправки (словарь).
        """
        try:
            # Преобразуем сообщение в JSON
            message_str = json.dumps(message)

            # Отправляем сообщение в Kafka
            self.producer.produce(topic, value=message_str.encode("utf-8"))

            # Ждем завершения отправки всех сообщений
            self.producer.flush()
        except KafkaException as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при отправке данных в Kafka: {str(e)}")
