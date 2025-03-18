from fastapi import APIRouter, Query
from typing import List, Optional
from src.schemas.stats import SensorStat
from src.repositories.analytics import AnalyticsRepository

router = APIRouter()


@router.get("/analytics", response_model=List[SensorStat])
async def get_analytics(
    sensor_id: Optional[str] = Query(None, description="ID сенсора"),
    start_time: Optional[int] = Query(None, description="Начало периода (timestamp)"),
    end_time: Optional[int] = Query(None, description="Конец периода (timestamp)"),
):
    result = await AnalyticsRepository().get(sensor_id, start_time, end_time)
    return result
