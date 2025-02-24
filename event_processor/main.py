import asyncio

from src.service.kafka_consumer import KafkaConsumerBase
from src.repositories.event import EventRepository

if __name__ == '__main__':
    kafka_config = {
        'bootstrap.servers': 'kafka:9093',
        'group.id': 'event-consumer-group',
        'auto.offset.reset': 'latest'
    }

    consumer = KafkaConsumerBase(config=kafka_config, topics=['sensor-events'])

    consumer.create_consumer()
    consumer.subscribe_to_topics()

    asyncio.run(consumer.consume_messages()) 
