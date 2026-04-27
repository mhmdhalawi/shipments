from fastapi import APIRouter

router = APIRouter(prefix="/shipments", tags=["shipments"])

@router.get("/")
async def get_shipments():
    return {"message": "List of shipments"}


@router.post("/")
async def create_shipment():
    return {"message": "Shipment created"}


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: int):
    return {"message": f"Details of shipment {shipment_id}"}