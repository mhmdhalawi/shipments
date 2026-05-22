from typing import TYPE_CHECKING

from .user import User
from uuid import UUID
from utils import generate_uuid7
from sqlmodel import Field, Relationship, DateTime as SADateTime, SQLModel
from sqlmodel._compat import SQLModelConfig
from sqlalchemy import Column
from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models import Shipment


class DeliveryPartnerLocation(SQLModel, table=True):
    model_config: SQLModelConfig = SQLModelConfig(arbitrary_types_allowed=True)

    __tablename__ = "delivery_partner_locations"  # type: ignore
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    delivery_partner_id: UUID = Field(foreign_key="delivery_partners.id")
    location: WKBElement = Field(
        sa_column=Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    )
    label: str | None = Field(default=None, max_length=100)

    delivery_partner: "DeliveryPartner" = Relationship(back_populates="locations")


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partners"  # type: ignore
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    service_radius_km: float | None = Field(default=None, ge=0)
    max_handling_capacity: int | None = Field(default=None, ge=0)

    locations: list["DeliveryPartnerLocation"] = Relationship(
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    shipments: list["Shipment"] = Relationship(
        back_populates="delivery_partner", sa_relationship_kwargs={"lazy": "selectin"}
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(SADateTime(timezone=True), nullable=False),
    )
