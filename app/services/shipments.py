# services/shipment_service.py
from uuid import UUID
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Sequence
from models.shipment import ShipmentStatus
from database import SessionDep
from models import Shipment
from .base import BaseService
from validation import ShipmentCreate, ShipmentUpdate


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(Shipment, session)

    async def get_all(self, seller_id: UUID) -> Sequence[Shipment]:
        result = await self.session.exec(
            select(Shipment).where(Shipment.seller_id == seller_id)
        )
        return result.all()

    async def get_by_id(self, shipment_id: UUID, seller_id: UUID) -> Shipment | None:
        result = await self.session.exec(
            select(Shipment).where(
                Shipment.id == shipment_id, Shipment.seller_id == seller_id
            )
        )
        return result.first()

    async def get_by_status(
        self, status: ShipmentStatus, seller_id: UUID
    ) -> Sequence[Shipment]:
        result = await self.session.exec(
            select(Shipment).where(
                Shipment.status == status, Shipment.seller_id == seller_id
            )
        )
        return result.all()

    async def create(self, shipment: ShipmentCreate, seller_id: UUID) -> Shipment:
        db_shipment = Shipment(**shipment.model_dump(), seller_id=seller_id)
        return await self._add(db_shipment)

    async def update(
        self, shipment_id: UUID, shipment: ShipmentUpdate, seller_id: UUID
    ) -> Shipment | None:
        db_shipment = await self.get_by_id(shipment_id, seller_id)
        if not db_shipment:
            return None
        for key, value in shipment.model_dump(exclude_unset=True).items():
            setattr(db_shipment, key, value)
        return await self._update(db_shipment)

    async def delete(self, shipment_id: UUID, seller_id: UUID) -> Shipment | None:
        db_shipment = await self.get_by_id(shipment_id, seller_id)
        if not db_shipment:
            return None
        return await self._delete(db_shipment)


def get_shipment_service(session: SessionDep) -> ShipmentService:
    return ShipmentService(session)


ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
