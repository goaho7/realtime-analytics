import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.service.kafka_consumer import KafkaConsumerBase
from src.api.routers import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer.subscribe_to_topics()
    task = asyncio.create_task(consumer.run_consumer())
    yield
    task.cancel()
    consumer.close()


app = FastAPI(lifespan=lifespan)


kafka_config = {
    "bootstrap.servers": "broker:29092",
    "acks": "all",
    "retries": 3,
    "group.id": "analytics_group",
}
topics = ["analytics-updates"]
consumer = KafkaConsumerBase(kafka_config, topics)

app.include_router(main_router)
