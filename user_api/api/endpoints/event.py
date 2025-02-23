from typing import Annotated
from fastapi import APIRouter, Depends

from schemas.event import EventSchema
from services.kafka_producer import KafkaProducerManager
from user_api.api.depensens import kafka_producer


router = APIRouter()

KAFKA_TOPIC = "sensor-events"

@router.post("")
def event(
    event: EventSchema,
    kafka_producer: KafkaProducerManager = Depends(kafka_producer)
):
    event_data = event.model_dump()
    kafka_producer.send_message(KAFKA_TOPIC, event_data)

    return {
        "status": "success",
        "message": "Данные успешно приняты",
        'data': event_data
    }
