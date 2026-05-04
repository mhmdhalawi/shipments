# routers/ai_router.py
from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import ShipmentServiceDep, AIServiceDep

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    shipment_id: UUID
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    ai: AIServiceDep,
    shipment_service: ShipmentServiceDep,
):
    shipment = await shipment_service.get_by_id(body.shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    answer = await ai.answer_about_shipment(shipment, body.question)
    return ChatResponse(answer=answer)
