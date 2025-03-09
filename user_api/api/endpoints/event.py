from fastapi import APIRouter, Depends

from schemas.event import EventSchema
from services.kafka_producer import KafkaProducerManager
from api.depensens import kafka_producer


router = APIRouter()

KAFKA_TOPIC = "sensor-events"


@router.post("")
def event(
    event: EventSchema, kafka_producer: KafkaProducerManager = Depends(kafka_producer)
):
    try:
        event_data = event.model_dump()
        kafka_producer.send_message(KAFKA_TOPIC, event_data)
    except Exception as e:
        return {"status": "error", "message": e}
    finally:
        kafka_producer.close()
