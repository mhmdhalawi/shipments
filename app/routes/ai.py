# routers/ai.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import AIServiceDep
from services import ShipmentServiceDep

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
            shipment_id
        ),
        "get_shipments_by_status": lambda status: shipment_service.get_by_status(
            status
        ),
    }

    answer = await ai.chat(body.question, handlers)
    return ChatResponse(answer=answer)
