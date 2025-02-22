from typing import Annotated
from fastapi import APIRouter, Depends

from user_api.schemas.event import EventSchema
from user_api.services.kafka_producer import KafkaProducerManager


router = APIRouter()
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # Адрес Kafka broker'а
KAFKA_TOPIC = "sensor-events"  # Название топика

@router.post("/event/")
def event(
    event: EventSchema,
    kafka_producer: Annotated[KafkaProducerManager, Depends(KafkaProducerManager(KAFKA_BOOTSTRAP_SERVERS))]
):
    event_data = event.model_dump()
    kafka_producer.send_message(KAFKA_TOPIC, event_data)

    return {
        "status": "success",
        "message": "Данные успешно приняты"
    }
