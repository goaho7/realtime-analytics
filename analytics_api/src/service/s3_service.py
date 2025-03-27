import json
import logging

from typing import Dict
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

from src.service.s3_client import S3Client
from src.repositories.analytics import AnalyticsRepository

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self, s3_client: S3Client, analytics_repo: AnalyticsRepository):
        self.s3_client = s3_client
        self.analytics_repo = analytics_repo

    async def upload_file(self) -> Dict[str, str]:
        now = datetime.now(timezone.utc)
        cutoff_timestamp = int((now - timedelta(days=7)).timestamp())

        logger.info(f"Fetching old events before {cutoff_timestamp}")
        events_list = await self.analytics_repo.fetch_old_events(cutoff_timestamp)
        if not events_list:
            logger.info("No old events found to archive")
            return {"message": "No old events to archive"}
        events_json = json.dumps(events_list, indent=2).encode("utf-8")

        file_name = f"{now.strftime('%Y%m%d_%H%M%S')}.json"

        try:
            try:
                logger.info(f"Uploading {len(events_list)} events to S3 as {file_name}")
                await self.s3_client.upload_file(file=events_json, file_name=file_name)
                logger.info(f"Successfully uploaded {file_name} to S3")
            except Exception as e:
                logger.error(f"Failed to upload {file_name} to S3: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to upload to S3: {str(e)}"
                )

            try:
                logger.info(f"Deleting {len(events_list)} old events from database")
                await self.analytics_repo.delete_old_events(cutoff_timestamp)
                logger.info(
                    f"Successfully deleted {len(events_list)} events from database"
                )
            except Exception as e:
                logger.error(f"Failed to delete old events from database: {str(e)}")
                return {
                    "message": f"Events archived to {file_name}, but failed to delete from database: {str(e)}",
                    "file_name": file_name,
                    "status": "partial_success",
                }

            return {
                "message": f"Events archived to {file_name} and deleted from database",
                "file_name": file_name,
                "status": "success",
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload to S3: {str(e)}"
            )
