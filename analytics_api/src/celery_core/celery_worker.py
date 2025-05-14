import logging
import sentry_sdk

from celery import Celery
from celery.schedules import crontab
from sentry_sdk.integrations.celery import CeleryIntegration

from settings.config import settings


logger = logging.getLogger(__name__)


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[CeleryIntegration()],
    traces_sample_rate=1.0,
    environment="production",
)

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.celery_core.tasks"],
)

celery_app.autodiscover_tasks(["src.celery_core.tasks"])


celery_app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=False,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "upload_file_daily": {
            "task": "src.celery_core.tasks.upload_daily_file",
            "schedule": crontab(hour=22, minute=24),
        },
    },
)
