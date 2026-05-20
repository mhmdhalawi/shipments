from pydantic import BaseModel, EmailStr, Field


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
