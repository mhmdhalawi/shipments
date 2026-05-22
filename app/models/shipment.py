from typing import TYPE_CHECKING

from uuid import UUID
from sqlalchemy import Column, DateTime as SADateTime, ForeignKey
from sqlmodel import DateTime, Field, Relationship
from sqlmodel._compat import SQLModelConfig
from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from datetime import datetime, timezone
from utils import generate_uuid7, generate_delivery_date
from validation import ShipmentStatus, BaseShipment

if TYPE_CHECKING:
    from models import Seller, DeliveryPartner


class Shipment(BaseShipment, table=True):
    model_config: SQLModelConfig = SQLModelConfig(arbitrary_types_allowed=True)

    __tablename__ = "shipments"  # type: ignore

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(SADateTime(timezone=True), nullable=False)
    )
    status: ShipmentStatus = ShipmentStatus.created
    estimated_delivery: datetime = Field(
        default_factory=generate_delivery_date,
        description="Estimated delivery date for the shipment",
        sa_column=Column(DateTime(timezone=True)),
    )

    destination: WKBElement = Field(
        sa_column=Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    )

    seller_id: UUID = Field(foreign_key="sellers.id")
    seller: "Seller" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )

    delivery_partner_id: UUID | None = Field(
        default=None,
        sa_column=Column(ForeignKey("delivery_partners.id", name="fk_shipments_delivery_partner_id"), nullable=True)
    )
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )
