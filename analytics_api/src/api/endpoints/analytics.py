from typing import List, Optional

from fastapi import APIRouter, Query, Depends

from src.schemas.stats import SensorStat
from src.repositories.analytics import AnalyticsRepository
from src.service.s3_client import S3Client
from src.api.depensens import get_s3_client


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
