from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from settings.db_setting import async_session_maker


class AbstractRepository(ABC):

    @abstractmethod
    async def get(self, obj_id):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data):
        raise NotImplementedError

    @abstractmethod
    async def update(self, data, obj_id):
        raise NotImplementedError

    @abstractmethod
    async def remove(self, obj_id):
        raise NotImplementedError


class SQLAlchemyBaseRepository(AbstractRepository):
    model = None

    async def get(self, obj_id: int):
        
        async with async_session_maker() as session:
            db_obj = await session.execute(select(self.model).where(self.model.id == obj_id))
            result = db_obj.scalars().first()
            if result is None:
                raise ValueError(f"Object with ID {obj_id} not found.")
            return result

    async def get_all(self, limit: int = 100, offset: int = 0):
        
        async with async_session_maker() as session:
            res = await session.execute(select(self.model).limit(limit).offset(offset))
            return res.scalars().all()

    async def create(self, data: dict):
        
        async with async_session_maker() as session:
            try:
                stmt = insert(self.model).values(**data).returning(self.model)
                res = await session.execute(stmt)
                await session.commit()
                return res.scalar()
            except IntegrityError as e:
                await session.rollback()
                raise ValueError(f"Database integrity error: {e}") from e

    async def update(self, data: dict, obj_id: int):
        
        async with async_session_maker() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == obj_id)
                .values(**data)
                .returning(self.model)
            )
            res = await session.execute(stmt)
            await session.commit()
            updated_obj = res.scalar()
            if updated_obj is None:
                raise ValueError(f"Object with ID {obj_id} not found.")
            return updated_obj

    async def remove(self, obj_id: int):
        
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == obj_id)
            res = await session.execute(stmt)
            await session.commit()
            if res.rowcount == 0:
                raise ValueError(f"Object with ID {obj_id} not found.")
            return True
