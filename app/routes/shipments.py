from uuid import UUID
from typing import Sequence
from fastapi import APIRouter, HTTPException, status

from models import Shipment
from validation import ShipmentCreate, ShipmentUpdate
from services import ShipmentServiceDep


router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.get("/")
async def get_shipments(service: ShipmentServiceDep) -> Sequence[Shipment]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment: ShipmentCreate, service: ShipmentServiceDep
) -> Shipment:
    return await service.create(shipment)


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: UUID, service: ShipmentServiceDep) -> Shipment:
    db_shipment = await service.get_by_id(shipment_id)

    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )

    return db_shipment


@router.patch("/{shipment_id}")
async def update_shipment(
    shipment_id: UUID, shipment: ShipmentUpdate, service: ShipmentServiceDep
) -> Shipment:
    db_shipment = await service.update(shipment_id, shipment)

    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )

    return db_shipment


@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: UUID, service: ShipmentServiceDep):
    db_shipment = await service.delete(shipment_id)

    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )

    return {"message": f"Shipment {shipment_id} deleted successfully"}
