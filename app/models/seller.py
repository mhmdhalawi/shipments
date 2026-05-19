from typing import TYPE_CHECKING
from sqlmodel import Relationship, Field
from utils import generate_uuid7
from uuid import UUID
from .user import User

if TYPE_CHECKING:
    from models import Shipment


class Seller(User, table=True):
    __tablename__ = "sellers"  # type: ignore
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)

    shipments: list["Shipment"] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
