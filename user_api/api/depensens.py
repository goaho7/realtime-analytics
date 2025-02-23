from services.kafka_producer import KafkaProducerManager

KAFKA_BOOTSTRAP_SERVERS = "kafka:9093"

def kafka_producer():
    return KafkaProducerManager(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
