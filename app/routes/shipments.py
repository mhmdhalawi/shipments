from uuid import UUID
from typing import Sequence
from fastapi import APIRouter, HTTPException, status
from models import Shipment
from services import CurrentSellerDep
from validation import ShipmentCreate, ShipmentOut, ShipmentUpdate
from services import ShipmentServiceDep


router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ShipmentOut)
async def create_shipment(
    shipment: ShipmentCreate, service: ShipmentServiceDep, seller: CurrentSellerDep
) -> Shipment:
    return await service.create(shipment, seller.id)


@router.get("/", response_model=list[ShipmentOut])
async def get_shipments(
    service: ShipmentServiceDep, seller: CurrentSellerDep
) -> Sequence[Shipment]:
    return await service.get_all(seller.id)


@router.patch("/{shipment_id}", response_model=ShipmentOut)
async def update_shipment(
    shipment_id: UUID,
    shipment: ShipmentUpdate,
    service: ShipmentServiceDep,
    seller: CurrentSellerDep,
) -> Shipment:
    db_shipment = await service.update(shipment_id, shipment, seller.id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )
    return db_shipment


@router.delete("/{shipment_id}")
async def delete_shipment(
    shipment_id: UUID, service: ShipmentServiceDep, seller: CurrentSellerDep
):
    db_shipment = await service.delete(shipment_id, seller.id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )
    return {"message": f"Shipment {shipment_id} deleted successfully"}
