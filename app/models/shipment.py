from typing import Optional
from uuid import UUID
import uuid_utils as uuid
from enum import Enum
from random import randint
from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta


def random_number():
    return randint(11000, 11999)


def generate_uuid7():
    return uuid.uuid7()


def generate_delivery_date():
    return datetime.now() + timedelta(days=randint(1, 10))


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


class Shipment(BaseShipment, table=True):
    __tablename__ = "shipments"  # type: ignore

    id: Optional[UUID] = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique identifier for the shipment",
    )
    status: ShipmentStatus = ShipmentStatus.created
    estimated_delivery: Optional[datetime] = Field(
        default_factory=generate_delivery_date,
        description="Estimated delivery date for the shipment",
    )


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseShipment):
    status: ShipmentStatus = Field(
        default=ShipmentStatus.created, description="Status of the shipment"
    )
    estimated_delivery: Optional[datetime] = Field(
        default_factory=None,
        description="Estimated delivery date for the shipment",
    )
