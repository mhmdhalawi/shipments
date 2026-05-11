from uuid import UUID
from sqlalchemy import Column
from sqlmodel import DateTime, Field
from datetime import datetime
from utils import generate_uuid7, generate_delivery_date
from validation import ShipmentStatus, BaseShipment


class Shipment(BaseShipment, table=True):
    __tablename__ = "shipments"  # type: ignore

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
    )
    status: ShipmentStatus = ShipmentStatus.created
    estimated_delivery: datetime = Field(
        default_factory=generate_delivery_date,
        description="Estimated delivery date for the shipment",
        sa_column=Column(DateTime(timezone=True)),
    )
