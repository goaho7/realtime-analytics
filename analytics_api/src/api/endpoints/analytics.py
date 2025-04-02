from typing import Annotated, List, Optional
from datetime import datetime

from fastapi import APIRouter, Query, Depends

from src.schemas.stats import SensorStat
from src.repositories.analytics import AnalyticsRepository
from src.service.s3_service import S3Service
from src.service.s3_client import S3Client
from src.api.depensens import get_s3_service, get_s3_client
from src.celery_core.tasks import upload_daily_file


router = APIRouter()


@router.get("/analytics", response_model=List[SensorStat])
async def get_analytics(
    sensor_id: Optional[str] = Query(None, description="ID сенсора"),
    start_time: Optional[int] = Query(None, description="Начало периода (timestamp)"),
    end_time: Optional[int] = Query(None, description="Конец периода (timestamp)"),
):
    result = await AnalyticsRepository().get(sensor_id, start_time, end_time)
    return result


@router.get("/list-files")
async def get_list_files(
    s3_client: S3Client = Depends(get_s3_client),
    start_time: str = Query(None, description="Format: DD-MM-YYYY"),
    end_time: str = Query(None, description="Format: DD-MM-YYYY"),
):
    return await s3_client.list_files(start_time, end_time)


@router.get("/get-file")
async def get_file(file_name: str, s3_client: S3Client = Depends(get_s3_client)):
    return await s3_client.download_file(file_name)


# @router.get("/test")
# async def test(s3_service: Annotated[S3Service, Depends(get_s3_service)]):
#     return await s3_service.upload_file()


# @router.get("/trigger-task")
# async def trigger_task():
#     task = upload_daily_file.delay()
#     return {"message": "Task triggered", "task_id": task.id}
