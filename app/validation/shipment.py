from enum import Enum

from datetime import datetime
from sqlmodel import SQLModel, Field


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
    destination: str = Field(
        description="Destination as WKT point, e.g. 'POINT(lng lat)'"
    )


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(SQLModel):
    content: str | None = Field(default=None, min_length=1, max_length=100)
    weight: float | None = Field(default=None, gt=0, lt=25)
    destination: str | None = None
    status: ShipmentStatus | None = Field(
        default=None, description="Status of the shipment"
    )
    estimated_delivery: datetime | None = Field(
        default=None,
        description="Estimated delivery date for the shipment",
    )
