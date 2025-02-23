import json
from confluent_kafka import Producer, KafkaException
from fastapi import HTTPException


class KafkaProducerManager:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send_message(self, topic: str, message: dict):
        try:
            message_str = json.dumps(message)
            self.producer.produce(topic, value=message_str.encode("utf-8"))
            self.producer.flush()
        except KafkaException as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при отправке данных в Kafka: {str(e)}")
