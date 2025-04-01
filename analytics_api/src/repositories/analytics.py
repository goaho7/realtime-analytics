import logging

from fastapi import HTTPException
from typing import Optional, List, Dict, Union
from sqlalchemy import select, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import BinaryExpression

from settings.db_setting import async_session_maker
from src.models.event import Event
from src.schemas.stats import SensorStat

logger = logging.getLogger(__name__)


class AnalyticsRepository:
    model = Event

    async def get(
        self,
        sensor_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict[str, Union[float, int, str]]]:
        async with async_session_maker() as session:
            try:
                query = (
                    select(
                        self.model.sensor_id,
                        func.avg(self.model.temperature).label("avg_temperature"),
                        func.avg(self.model.humidity).label("avg_humidity"),
                        func.avg(self.model.noise_level).label("avg_noise_level"),
                        func.avg(self.model.air_quality_index).label(
                            "avg_air_quality_index"
                        ),
                        func.min(self.model.timestamp).label("min_timestamp"),
                        func.max(self.model.timestamp).label("max_timestamp"),
                    )
                    .where(
                        (
                            (self.model.sensor_id == sensor_id)
                            if sensor_id is not None
                            else True
                        ),
                        (
                            (self.model.timestamp >= start_time)
                            if start_time is not None
                            else True
                        ),
                        (
                            (self.model.timestamp <= end_time)
                            if end_time is not None
                            else True
                        ),
                    )
                    .group_by(self.model.sensor_id)
                )

                result = await session.execute(query)
                rows = result.mappings().all()

                if not rows:
                    raise HTTPException(
                        status_code=404, detail="No data found for the given filters"
                    )

                return [
                    {
                        "sensor_id": row["sensor_id"],
                        "avg_temperature": float(round(row["avg_temperature"], 2)),
                        "avg_humidity": float(round(row["avg_humidity"], 2)),
                        "avg_noise_level": float(round(row["avg_noise_level"], 2)),
                        "avg_air_quality_index": float(
                            round(row["avg_air_quality_index"], 2)
                        ),
                        "min_timestamp": row["min_timestamp"],
                        "max_timestamp": row["max_timestamp"],
                    }
                    for row in rows
                ]
            except SQLAlchemyError as e:
                logger.error(f"Database error in get: {str(e)}")
                raise HTTPException(status_code=500, detail="Database error occurred")

    async def fetch_old_events(self, cutoff_timestamp: int) -> List[SensorStat]:
        async with async_session_maker() as session:
            try:
                stmt = (
                    select(self.model)
                    .where(self._old_events_filter(cutoff_timestamp))
                    .execution_options(yield_per=1000)
                )
                result = await session.stream(stmt)

                events_list = []
                async for event in result.scalars():
                    events_list.append(
                        {
                            "id": event.id,
                            "sensor_id": event.sensor_id,
                            "temperature": event.temperature,
                            "humidity": event.humidity,
                            "noise_level": event.noise_level,
                            "air_quality_index": event.air_quality_index,
                            "timestamp": event.timestamp,
                        }
                    )

                logger.info(
                    f"Fetched {len(events_list)} old events before {cutoff_timestamp}"
                )
                return events_list
            except SQLAlchemyError as e:
                logger.error(f"Database error in fetch_old_events: {str(e)}")
                raise HTTPException(status_code=500, detail="Database error occurred")

    async def delete_old_events(self, cutoff_timestamp: int) -> None:
        async with async_session_maker() as session:
            try:
                batch_size = 1000
                while True:
                    select_stmt = (
                        select(self.model.id)
                        .where(self._old_events_filter(cutoff_timestamp))
                        .limit(batch_size)
                    )
                    select_result = await session.execute(select_stmt)
                    ids_to_delete = select_result.scalars().all()

                    if not ids_to_delete:
                        break

                    delete_stmt = delete(self.model).where(
                        self.model.id.in_(ids_to_delete)
                    )
                    await session.execute(delete_stmt)
                    await session.commit()

                    logger.info(
                        f"Deleted {len(ids_to_delete)} old events before {cutoff_timestamp}"
                    )
            except SQLAlchemyError as e:
                logger.error(f"Database error in delete_old_events: {str(e)}")
                await session.rollback()
                raise HTTPException(status_code=500, detail="Database error occurred")

    def _old_events_filter(self, cutoff_timestamp: int) -> BinaryExpression:
        return self.model.timestamp < cutoff_timestamp
