import math

from fastapi import HTTPException
from typing import Optional
from sqlalchemy import select

from settings.db_setting import async_session_maker
from src.models.event import Event


class AnalyticsRepository:
    model = Event
    
    async def get(self, sensor_id: Optional[str], start_time: Optional[int], end_time: Optional[int]):

        async with async_session_maker() as session:
            query = select(self.model)
    
            if sensor_id is not None:
                query = query.filter(self.model.sensor_id == sensor_id)
            if start_time is not None:
                query = query.filter(self.model.timestamp >= start_time)
            if end_time is not None:
                query = query.filter(self.model.timestamp <= end_time)
        
            result = await session.execute(query)
            results = result.scalars().all()
        
            if not results:
                raise HTTPException(status_code=404, detail="No data found for the given filters")
        
            stats = {}
            for row in results:
                if row.sensor_id not in stats:
                    stats[row.sensor_id] = {
                        "temperature_sum": 0,
                        "humidity_sum": 0,
                        "noise_level_sum": 0,
                        "air_quality_index_sum": 0,
                        "count": 0,
                        "min_timestamp": math.inf,
                        "max_timestamp": -math.inf
                    }
        
                stats[row.sensor_id]["temperature_sum"] += row.temperature
                stats[row.sensor_id]["humidity_sum"] += row.humidity
                stats[row.sensor_id]["noise_level_sum"] += row.noise_level
                stats[row.sensor_id]["air_quality_index_sum"] += row.air_quality_index
                stats[row.sensor_id]["count"] += 1
                stats[row.sensor_id]["min_timestamp"] = min(stats[row.sensor_id]["min_timestamp"], row.timestamp)
                stats[row.sensor_id]["max_timestamp"] = max(stats[row.sensor_id]["max_timestamp"], row.timestamp)
        
            response = []
            for sensor_id, data in stats.items():
                avg_temperature = data["temperature_sum"] / data["count"]
                avg_humidity = data["humidity_sum"] / data["count"]
                avg_noise_level = data["noise_level_sum"] / data["count"]
                avg_air_quality_index = data["air_quality_index_sum"] / data["count"]
        
                response.append({
                    "sensor_id": sensor_id,
                    "avg_temperature": round(avg_temperature, 2),
                    "avg_humidity": round(avg_humidity, 2),
                    "avg_noise_level": round(avg_noise_level, 2),
                    "avg_air_quality_index": round(avg_air_quality_index, 2),
                    "min_timestamp": data["min_timestamp"],
                    "max_timestamp": data["max_timestamp"]
                })
        
            return response
