from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/shipments", tags=["shipments"])

class Shipment(BaseModel):
    content: str
    weight: float
    status: str

@router.get("/")
async def get_shipments():
    return {"message": "List of shipments"}


@router.post("/")
async def create_shipment(shipment: Shipment)-> Shipment:

    if shipment.weight <= 0 or shipment.weight > 25:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Weight must be between 0 and 25 kg")

    return  Shipment(content=shipment.content, weight=shipment.weight, status="created")


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: int):

    if not shipment_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Shipment ID is required")

    return {"message": f"Details of shipment {shipment_id}"}