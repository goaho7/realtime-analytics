import logging

from celery import Celery
from celery.schedules import crontab
from settings.config import settings
from src.repositories.analytics import AnalyticsRepository
from src.service.s3_service import S3Service
from src.service.s3_client import S3Client

logger = logging.getLogger(__name__)


# celery_app.autodiscover_tasks()

# celery_app.conf.update(
#     timezone="Europe/Moscow",
#     enable_utc=False,
#     broker_connection_retry_on_startup=True,
#     beat_schedule={
#         "upload_file_daily": {
#             "task": "src.celery_core.tasks.upload_daily_file",
#             "schedule": crontab(hour=16, minute=53),
#         },
#     },
# )


celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["celery_core.tasks"],
)

celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "every_minute": {
        "task": "celery_core.tasks.add",
        "schedule": crontab(minute="*/1"),
        "args": (4, 6),
    },
}
