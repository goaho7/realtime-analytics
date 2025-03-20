import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.service.kafka_consumer import KafkaConsumerBase
from src.api.routers import main_router
from src.kafka_config import kafka_config, kafka_topics


consumer = KafkaConsumerBase(kafka_config, kafka_topics)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await consumer.subscribe_to_topics()
    task = asyncio.create_task(consumer.run_consumer())
    yield
    task.cancel()
    consumer.close()


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
