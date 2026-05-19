from .user import User
from uuid import UUID
from utils import generate_uuid7
from sqlmodel import Field
from sqlalchemy import Column
from geoalchemy2 import Geography


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partners"  # type: ignore
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    location: str | None = Field(
        default=None,
        sa_column=Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    )
    service_radius_km: float | None = Field(default=None, ge=0)
