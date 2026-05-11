from enum import Enum

from datetime import datetime
from sqlmodel import SQLModel, Field
from utils import generate_delivery_date, random_number


class ShipmentStatus(str, Enum):
    created = "created"
    in_transit = "in_transit"
    delivered = "delivered"


class BaseShipment(SQLModel):
    content: str = Field(
        min_length=1,
        max_length=100,
        description="Content description of the shipment",
    )
    weight: float = Field(gt=0, lt=25, description="Weight must be between 0 and 25 kg")
    destination: int = Field(
        default_factory=random_number, description="Destination code for the shipment"
    )


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(SQLModel):
    content: str | None = Field(default=None, min_length=1, max_length=100)
    weight: float | None = Field(default=None, gt=0, lt=25)
    destination: int | None = None
    status: ShipmentStatus = Field(
        default=ShipmentStatus.created, description="Status of the shipment"
    )
    estimated_delivery: datetime = Field(
        default_factory=generate_delivery_date,
        description="Estimated delivery date for the shipment",
    )
