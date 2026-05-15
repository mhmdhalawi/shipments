from uuid import UUID
from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, status
from models import Shipment
from services import get_current_seller, CurrentSellerDep
from validation import ShipmentCreate, ShipmentUpdate
from services import ShipmentServiceDep


router = APIRouter(
    prefix="/shipments", tags=["shipments"], dependencies=[Depends(get_current_seller)]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment: ShipmentCreate, service: ShipmentServiceDep, seller: CurrentSellerDep
) -> Shipment:
    return await service.create(shipment, seller.id)


@router.get("/")
async def get_shipments(
    service: ShipmentServiceDep, seller: CurrentSellerDep
) -> Sequence[Shipment]:
    return await service.get_all(seller.id)


@router.patch("/{shipment_id}")
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
