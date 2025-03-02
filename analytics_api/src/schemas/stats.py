from pydantic import BaseModel


class SensorStat(BaseModel):
    sensor_id: str
    avg_temperature: float
    avg_humidity: float
    avg_noise_level: float
    avg_air_quality_index: float
    min_timestamp: int
    max_timestamp: int
