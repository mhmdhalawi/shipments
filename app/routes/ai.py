# routers/ai.py
from fastapi import APIRouter
from pydantic import BaseModel
from models.shipment import ShipmentCreate, ShipmentUpdate
from services import AIServiceDep, ShipmentServiceDep
from uuid import UUID

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    ai: AIServiceDep,
    shipment_service: ShipmentServiceDep,
):

    handlers = {
        "get_all_shipments": lambda: shipment_service.get_all(),
        "get_shipment_by_id": lambda shipment_id: shipment_service.get_by_id(
            UUID(shipment_id)
        ),
        "get_shipments_by_status": lambda status: shipment_service.get_by_status(
            status
        ),
        "create_shipment": lambda content, weight: shipment_service.create(
            ShipmentCreate(content=content, weight=weight)
        ),
        "update_shipment": lambda shipment_id, **kwargs: shipment_service.update(
            UUID(shipment_id), ShipmentUpdate(**kwargs)
        ),
        "delete_shipment": lambda shipment_id: shipment_service.delete(
            UUID(shipment_id)
        ),
    }

    answer = await ai.chat(body.question, handlers)
    return ChatResponse(answer=answer)
