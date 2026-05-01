# services/shipment_service.py
from uuid import UUID
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Sequence
from database import SessionDep
from models import Shipment, ShipmentCreate, ShipmentUpdate


class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> Sequence[Shipment]:
        result = await self.session.exec(select(Shipment))
        return result.all()

    async def get_by_id(self, shipment_id: UUID) -> Shipment | None:
        return await self.session.get(Shipment, shipment_id)

    async def create(self, shipment: ShipmentCreate) -> Shipment:
        db_shipment = Shipment(content=shipment.content, weight=shipment.weight)
        self.session.add(db_shipment)
        await self.session.commit()
        return db_shipment

    async def update(
        self, shipment_id: UUID, shipment: ShipmentUpdate
    ) -> Shipment | None:
        db_shipment = await self.session.get(Shipment, shipment_id)
        if not db_shipment:
            return None
        for key, value in shipment.model_dump(exclude_unset=True).items():
            setattr(db_shipment, key, value)
        self.session.add(db_shipment)
        await self.session.commit()
        return db_shipment

    async def delete(self, shipment_id: UUID) -> Shipment | None:
        db_shipment = await self.session.get(Shipment, shipment_id)
        if not db_shipment:
            return None
        await self.session.delete(db_shipment)
        await self.session.commit()
        return db_shipment


#  dependency injection setup
def get_shipment_service(session: SessionDep) -> ShipmentService:
    return ShipmentService(session)


ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
