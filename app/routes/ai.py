# routers/ai.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services import (
    AIServiceDep,
    ShipmentServiceDep,
    get_current_seller,
    CurrentSellerDep,
)
from validation import ShipmentCreate, ShipmentUpdate
from uuid import UUID

router = APIRouter(
    prefix="/ai", tags=["ai"], dependencies=[Depends(get_current_seller)]
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    ai: AIServiceDep,
    shipment_service: ShipmentServiceDep,
    seller: CurrentSellerDep,
):

    handlers = {
        "get_all_shipments": lambda: shipment_service.get_all(seller.id),
        "get_shipment_by_id": lambda shipment_id: shipment_service.get_by_id(
            UUID(shipment_id),
            seller.id,
        ),
        "get_shipments_by_status": lambda status: shipment_service.get_by_status(
            status, seller.id
        ),
        "create_shipment": lambda content, weight, destination: shipment_service.create(
            ShipmentCreate(content=content, weight=weight, destination=destination),
            seller.id,
        ),
        "update_shipment": lambda shipment_id, **kwargs: shipment_service.update(
            UUID(shipment_id),
            ShipmentUpdate(**kwargs),
            seller.id,
        ),
        "delete_shipment": lambda shipment_id: shipment_service.delete(
            UUID(shipment_id),
            seller.id,
        ),
    }

    answer = await ai.chat(body.question, handlers)
    return ChatResponse(answer=answer)
