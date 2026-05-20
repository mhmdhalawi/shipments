from uuid import UUID
from typing import Any
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


class BaseService:
    def __init__(self, model: type[SQLModel], session: AsyncSession):
        self.model = model
        self.session = session

    async def _get(self, id: UUID) -> Any:
        return await self.session.get(self.model, id)

    async def _add(self, entity: SQLModel) -> Any:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def _update(self, entity: SQLModel) -> Any:
        return await self._add(entity)

    async def _delete(self, entity: SQLModel) -> Any:
        await self.session.delete(entity)
        await self.session.commit()
        return entity
