from enum import Enum

from datetime import datetime
from uuid import UUID
from geojson_pydantic import Point
from pydantic import BaseModel, ConfigDict, field_validator
from shapely import get_x, get_y, wkb
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


class ShipmentCreate(BaseShipment):
    destination: str = Field(
        description="Destination as WKT point, e.g. 'POINT(lng lat)'"
    )


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


class ShipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    weight: float
    destination: Point
    status: ShipmentStatus
    estimated_delivery: datetime
    created_at: datetime
    seller_id: UUID
    delivery_partner_id: UUID | None

    @field_validator("destination", mode="before")
    @classmethod
    def parse_destination(cls, v):
        if hasattr(v, "data"):
            geom = wkb.loads(bytes(v.data))
            return {"type": "Point", "coordinates": [get_x(geom), get_y(geom)]}
        return v
