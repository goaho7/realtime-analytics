from src.models.event import Event
from src.repositories.base import SQLAlchemyBaseRepository


class EventRepository(SQLAlchemyBaseRepository):
    model = Event
