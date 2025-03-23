from typing import Annotated

from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from src.schemas.stats import SensorStat
from src.repositories.analytics import AnalyticsRepository
from src.service.s3_service import S3Service
from src.api.depensens import get_s3_service

router = APIRouter()


@router.get("/analytics", response_model=List[SensorStat])
async def get_analytics(
    sensor_id: Optional[str] = Query(None, description="ID сенсора"),
    start_time: Optional[int] = Query(None, description="Начало периода (timestamp)"),
    end_time: Optional[int] = Query(None, description="Конец периода (timestamp)"),
):
    result = await AnalyticsRepository().get(sensor_id, start_time, end_time)
    return result


@router.get("/test")
async def test(s3_service: Annotated[S3Service, Depends(get_s3_service)]):
    return await s3_service.upload_file()
