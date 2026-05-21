from uuid import UUID
from typing import Generic, TypeVar
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

ModelT = TypeVar("ModelT", bound=SQLModel)
EntityT = TypeVar("EntityT", bound=SQLModel)


class BaseService(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.model = model
        self.session = session

    async def _get(self, id: UUID) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def _add(self, entity: EntityT) -> EntityT:
        try:
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def _update(self, entity: EntityT) -> EntityT:
        return await self._add(entity)

    async def _delete(self, entity: EntityT) -> EntityT:
        try:
            await self.session.delete(entity)
            await self.session.commit()
            return entity
        except SQLAlchemyError:
            await self.session.rollback()
            raise
