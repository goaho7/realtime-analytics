from src.service.s3_client import S3Client
from src.service.s3_service import S3Service
from src.repositories.analytics import AnalyticsRepository
from settings.config import settings


def get_s3_service():
    analytics_repo = AnalyticsRepository()
    s3_client = S3Client(settings.get_s3_conf(), bucket_name="events-archive")
    return S3Service(s3_client, analytics_repo)
