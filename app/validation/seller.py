from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class SellerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Name of the seller")
    email: EmailStr = Field(
        min_length=5,
        max_length=100,
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class SellerResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}
