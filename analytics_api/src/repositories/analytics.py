import math

from fastapi import HTTPException
from typing import Optional, List, Dict, Union
from sqlalchemy import select, func

from settings.db_setting import async_session_maker
from src.models.event import Event


class AnalyticsRepository:
    model = Event

    async def get(
        self,
        sensor_id: Optional[str],
        start_time: Optional[int],
        end_time: Optional[int],
    ) -> List[Dict[str, Union[float, int, str]]]:

        # async with async_session_maker() as session:
        #     query = select(self.model)

        #     if sensor_id is not None:
        #         query = query.filter(self.model.sensor_id == sensor_id)
        #     if start_time is not None:
        #         query = query.filter(self.model.timestamp >= start_time)
        #     if end_time is not None:
        #         query = query.filter(self.model.timestamp <= end_time)

        #     result = await session.execute(query)
        #     results = result.scalars().all()

        async with async_session_maker() as session:
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
                    "avg_temperature": round(row["avg_temperature"], 2),
                    "avg_humidity": round(row["avg_humidity"], 2),
                    "avg_noise_level": round(row["avg_noise_level"], 2),
                    "avg_air_quality_index": round(row["avg_air_quality_index"], 2),
                    "min_timestamp": row["min_timestamp"],
                    "max_timestamp": row["max_timestamp"],
                }
                for row in rows
            ]
