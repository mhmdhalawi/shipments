from uuid import UUID
from datetime import datetime
from geojson_pydantic import Point
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from shapely import wkb, get_x, get_y
from validation.auth import TokenOut


class DeliveryPartnerBase(BaseModel):
    name: str = Field(
        min_length=1, max_length=100, description="Name of the delivery partner"
    )
    email: EmailStr = Field(
        min_length=5,
        max_length=100,
    )
    service_radius_km: float = Field(
        description="Service radius in kilometers for the delivery partner",
        ge=0,
    )
    max_handling_capacity: int = Field(
        description="Maximum number of shipments the delivery partner can handle simultaneously",
        ge=0,
    )


class DeliveryPartnerCreate(DeliveryPartnerBase):
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class DeliveryPartnerLocationCreate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    label: str | None = Field(default=None, max_length=100)


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str | None
    location: Point

    @field_validator("location", mode="before")
    @classmethod
    def parse_location(cls, v):
        if hasattr(v, "data"):
            geom = wkb.loads(bytes(v.data))
            return {"type": "Point", "coordinates": [get_x(geom), get_y(geom)]}
        return v


class DeliveryPartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    service_radius_km: float | None
    max_handling_capacity: int | None
    created_at: datetime
    locations: list[LocationOut]


class DeliveryPartnerAuthResponse(TokenOut):
    partner: DeliveryPartnerOut
