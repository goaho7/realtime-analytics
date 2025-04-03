import logging

from celery import shared_task

from settings.config import settings
from src.repositories.analytics import AnalyticsRepository
from src.service.s3_service import S3Service
from src.service.s3_client import S3Client
from src.celery_core.celery_worker import celery_app


logger = logging.getLogger(__name__)


# @celery_app.task
# def upload_daily_file():
#     try:
#         s3_client = S3Client(
#             settings.get_s3_conf(), getattr(settings, "BUCKET_NAME", "events-archive")
#         )
#         s3_service = S3Service(s3_client, AnalyticsRepository())
#         s3_service.upload_file()
#     except Exception as e:
#         logger.error(f"Failed to upload daily file: {str(e)}")


@celery_app.task
def add(x, y):
    logger.info(x + y)
    return x + y
