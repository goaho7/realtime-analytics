from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from settings.db_setting import Base


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(100))
    temperature: Mapped[float] = mapped_column()
    humidity: Mapped[float] = mapped_column()
    noise_level: Mapped[float] = mapped_column()
    air_quality_index: Mapped[int] = mapped_column()
    timestamp: Mapped[int] = mapped_column()
