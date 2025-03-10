from services.kafka_producer import KafkaProducerManager


CONFIG = {
    "bootstrap.servers": "broker:29092",
    "acks": "all",
    "retries": 3,
}


def kafka_producer():
    return KafkaProducerManager(CONFIG)
