from typing import Dict

from fastapi import Depends

from src.service.s3_client import S3Client
from src.service.s3_service import S3Service
from src.repositories.analytics import AnalyticsRepository
from settings.config import settings


def get_s3_service(
    analytics_repo: AnalyticsRepository = Depends(lambda: AnalyticsRepository()),
    s3_config: Dict[str, str] = Depends(lambda: settings.get_s3_conf()),
    bucket_name: str = Depends(
        lambda: getattr(settings, "BUCKET_NAME", "events-archive")
    ),
) -> S3Service:

    s3_client = S3Client(s3_config, bucket_name)
    return S3Service(s3_client, analytics_repo)
