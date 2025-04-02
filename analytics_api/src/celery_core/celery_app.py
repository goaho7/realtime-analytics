from celery import Celery
from celery.schedules import crontab
from settings.config import settings


celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.celery_core.tasks"],
)


celery_app.autodiscover_tasks()

celery_app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=False,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "upload_file_daily": {
            "task": "src.celery_core.tasks.upload_daily_file",
            "schedule": crontab(hour=16, minute=53),
        },
    },
)
