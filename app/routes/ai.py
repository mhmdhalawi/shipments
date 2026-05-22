# routers/ai.py
from fastapi import APIRouter
from pydantic import BaseModel
from models import Seller
from services import (
    AIServiceDep,
    ShipmentService,
    ShipmentServiceDep,
    CurrentSellerDep,
)
from validation import ShipmentCreate, ShipmentStatus, ShipmentUpdate
from uuid import UUID

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


def build_shipment_handlers(shipment_service: ShipmentService, seller: Seller):
    async def get_all_shipments():
        return await shipment_service.get_all(seller.id)

    async def get_shipment_by_id(shipment_id: str):
        return await shipment_service.get_by_id(UUID(shipment_id), seller.id)

    async def get_shipments_by_status(status: str):
        return await shipment_service.get_by_status(ShipmentStatus(status), seller.id)

    async def create_shipment(content: str, weight: float, destination: str):
        shipment = ShipmentCreate(
            content=content,
            weight=weight,
            destination=destination,
        )
        return await shipment_service.create(shipment, seller.id)

    async def update_shipment(shipment_id: str, **kwargs):
        shipment = ShipmentUpdate(**kwargs)
        return await shipment_service.update(UUID(shipment_id), shipment, seller.id)

    async def delete_shipment(shipment_id: str):
        return await shipment_service.delete(UUID(shipment_id), seller.id)

    return {
        "get_all_shipments": get_all_shipments,
        "get_shipment_by_id": get_shipment_by_id,
        "get_shipments_by_status": get_shipments_by_status,
        "create_shipment": create_shipment,
        "update_shipment": update_shipment,
        "delete_shipment": delete_shipment,
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    ai: AIServiceDep,
    shipment_service: ShipmentServiceDep,
    seller: CurrentSellerDep,
):
    handlers = build_shipment_handlers(shipment_service, seller)
    answer = await ai.chat(body.question, handlers)
    return ChatResponse(answer=answer)
