from enum import Enum
from random import randint
from pydantic import BaseModel, Field


def random_number():
    return randint(11000, 11999)


class ShipmentStatus(str, Enum):
    created = "created"
    in_transit = "in_transit"
    delivered = "delivered"


class BaseShipment(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=100,
        description="Content description of the shipment",
    )
    weight: float = Field(gt=0, lt=25, description="Weight must be between 0 and 25 kg")
    destination: int = Field(
        default_factory=random_number, description="Destination code for the shipment"
    )


class Shipment(BaseShipment):
    id: int = Field(
        default_factory=random_number,
        description="Unique identifier for the shipment",
    )
    status: ShipmentStatus = ShipmentStatus.created


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseShipment):
    status: ShipmentStatus = Field(
        default=ShipmentStatus.created, description="Status of the shipment"
    )
