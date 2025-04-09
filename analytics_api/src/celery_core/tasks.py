import logging

from asgiref.sync import async_to_sync

from celery import shared_task

from settings.config import settings
from src.repositories.analytics import AnalyticsRepository
from src.service.s3_service import S3Service
from src.service.s3_client import S3Client


logger = logging.getLogger(__name__)


@shared_task
def upload_daily_file():
    try:
        s3_client = S3Client(
            settings.get_s3_conf(), getattr(settings, "BUCKET_NAME", "events-archive")
        )
        s3_service = S3Service(s3_client, AnalyticsRepository())
        async_to_sync(s3_service.upload_file)()
    except Exception as e:
        logger.error(f"Failed to upload daily file: {str(e)}")
