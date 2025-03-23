import json
from typing import Dict
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

from src.service.s3_client import S3Client
from src.repositories.analytics import AnalyticsRepository


class S3Service:
    def __init__(self, s3_client: S3Client, analytics_repo: AnalyticsRepository):
        self.s3_client = s3_client
        self.analytics_repo = analytics_repo

    async def upload_file(self) -> Dict[str, str]:
        now = datetime.now(timezone.utc)
        cutoff_timestamp = int((now - timedelta(days=7)).timestamp())

        events_list = await self.analytics_repo.fetch_old_events(cutoff_timestamp)
        if not events_list:
            return {"message": "No old events to archive"}
        events_json = json.dumps(events_list, indent=2).encode("utf-8")

        file_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            await self.s3_client.upload_file(file=events_json, file_name=file_name)
            await self.analytics_repo.delete_old_events(cutoff_timestamp)

            return {
                "message": f"Events archived to {file_name} and deleted from database"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload to S3: {str(e)}"
            )
