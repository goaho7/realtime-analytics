from src.service.kafka_producer import KafkaProducerManager
from src.repositories.event import EventRepository
from datetime import datetime
import logging


logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


KAFKA_TOPIC = "analytics-updates"
CONFIG = {
    "bootstrap.servers": "broker:29092",
    "acks": "all",
    "retries": 3,
}


async def processing(message_data):
    await EventRepository().create(message_data)

    try:
        kafka_producer = KafkaProducerManager(CONFIG)
        event_time = datetime.now().isoformat()
        await kafka_producer.send_message(KAFKA_TOPIC, {"event_time": event_time})
    except Exception as e:
        logging.info(e)
        return {"status": "error", "message": e}
    finally:
        kafka_producer.close()
