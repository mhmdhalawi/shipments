from fastapi import APIRouter, HTTPException, status
from models.shipment import Shipment, ShipmentCreate, ShipmentUpdate


router = APIRouter(prefix="/shipments", tags=["shipments"])

shipments: list[Shipment] = []


@router.get("/")
async def get_shipments():
    return {"message": "List of shipments"}


# document the status code for swagger


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Shipment created successfully"}
    },
)
async def create_shipment(shipment: ShipmentCreate) -> Shipment:
    shipments.append(Shipment(content=shipment.content, weight=shipment.weight))
    return Shipment(content=shipment.content, weight=shipment.weight)


@router.patch("/{shipment_id}")
async def update_shipment(shipment_id: int, shipment: ShipmentUpdate) -> Shipment:

    if shipment_id not in [s.id for s in shipments]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid shipment ID"
        )

    # loop in shipments and update the shipment with the given id
    for s in shipments:
        if s.id == shipment_id:
            s.content = shipment.content
            s.weight = shipment.weight
            s.status = shipment.status

    return Shipment(
        id=shipment_id,
        content=shipment.content,
        weight=shipment.weight,
        status=shipment.status,
    )


@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: int):

    if shipment_id not in [s.id for s in shipments]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid shipment ID"
        )

    shipments[:] = [s for s in shipments if s.id != shipment_id]

    return {"message": f"Shipment {shipment_id} deleted successfully"}


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: int):

    if not shipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Shipment ID is required"
        )

    return {"message": f"Details of shipment {shipment_id}"}
