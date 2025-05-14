import asyncio
import sentry_sdk

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from src.service.kafka_consumer import KafkaConsumerBase
from src.api.routers import main_router
from src.kafka_config import kafka_config, kafka_topics
from src.service.s3_service import S3Service
from src.service.s3_client import S3Client
from src.repositories.analytics import AnalyticsRepository
from settings.config import settings


consumer = KafkaConsumerBase(kafka_config, kafka_topics)

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    environment="production",
    send_default_pii=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer.subscribe_to_topics()
    task = asyncio.create_task(consumer.run_consumer())

    s3_client = S3Client(
        settings.get_s3_conf(), getattr(settings, "BUCKET_NAME", "events-archive")
    )
    app.state.s3_client = s3_client
    app.state.s3_service = S3Service(s3_client, AnalyticsRepository())

    yield

    task.cancel()
    consumer.close()
    del app.state.s3_client
    del app.state.s3_service


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)

app = SentryAsgiMiddleware(app)
