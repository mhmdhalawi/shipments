from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from database import SessionDep
from models import Shipment, ShipmentCreate, ShipmentUpdate
from typing import Sequence


router = APIRouter(prefix="/shipments", tags=["shipments"])

shipments: list[Shipment] = []


@router.get("/")
async def get_shipments(session: SessionDep) -> Sequence[Shipment]:
    result = await session.exec(select(Shipment))
    return result.all()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Shipment created successfully"}
    },
)
async def create_shipment(shipment: ShipmentCreate, session: SessionDep) -> Shipment:
    db_shipment = Shipment(content=shipment.content, weight=shipment.weight)
    session.add(db_shipment)
    await session.commit()
    return db_shipment


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: UUID, session: SessionDep):

    if not shipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Shipment ID is required"
        )

    db_shipment = await session.get(Shipment, shipment_id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )

    return db_shipment


@router.patch("/{shipment_id}")
async def update_shipment(
    shipment_id: UUID, shipment: ShipmentUpdate, session: SessionDep
) -> Shipment:
    db_shipment = await session.get(Shipment, shipment_id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )

    for key, value in shipment.model_dump(exclude_unset=True).items():
        setattr(db_shipment, key, value)

    session.add(db_shipment)
    await session.commit()
    return db_shipment


@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: UUID, session: SessionDep):

    db_shipment = await session.get(Shipment, shipment_id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
        )

    await session.delete(db_shipment)
    await session.commit()

    return {"message": f"Shipment {shipment_id} deleted successfully"}
