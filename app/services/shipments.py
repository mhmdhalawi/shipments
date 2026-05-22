# services/shipment_service.py
from uuid import UUID
from fastapi import Depends, HTTPException, status
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape
from shapely import wkt
from shapely.geometry import Point
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Sequence
from models.shipment import ShipmentStatus
from database import SessionDep
from models import Shipment
from .base import BaseService
from validation import ShipmentCreate, ShipmentUpdate


class ShipmentService(BaseService[Shipment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Shipment, session)

    def _parse_destination(self, destination: str) -> WKBElement:
        try:
            geometry = wkt.loads(destination)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Destination must be a valid WKT point, e.g. 'POINT(lng lat)'",
            )

        if not isinstance(geometry, Point):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Destination must be a WKT point, e.g. 'POINT(lng lat)'",
            )

        return from_shape(geometry, srid=4326)

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
        shipment_data = shipment.model_dump()
        shipment_data["destination"] = self._parse_destination(shipment.destination)
        shipment_data["seller_id"] = seller_id

        db_shipment = Shipment.model_validate(shipment_data)
        return await self._add(db_shipment)

    async def update(
        self, shipment_id: UUID, shipment: ShipmentUpdate, seller_id: UUID
    ) -> Shipment | None:
        db_shipment = await self.get_by_id(shipment_id, seller_id)
        if not db_shipment:
            return None
        shipment_data = shipment.model_dump(exclude_unset=True)
        if "destination" in shipment_data and shipment_data["destination"] is not None:
            shipment_data["destination"] = self._parse_destination(
                shipment_data["destination"]
            )

        for key, value in shipment_data.items():
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
