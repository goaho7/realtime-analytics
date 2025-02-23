from pydantic import BaseModel
from pydantic.config import ConfigDict


class EventSchema(BaseModel):
    sensor_id: str  # Уникальный ID датчика
    temperature: float  # Температура в градусах Цельсия
    humidity: float  # Влажность в процентах
    noise_level: float  # Уровень шума в децибелах (dB)
    air_quality_index: int  # Индекс качества воздуха (от 0 до 500)
    timestamp: int  # Временная метка сбора данных

    model_config = ConfigDict(from_attributes=True)
