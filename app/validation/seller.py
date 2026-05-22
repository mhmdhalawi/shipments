from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict
from validation.auth import TokenOut


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


class SellerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    created_at: datetime


class SellerAuthResponse(TokenOut):
    seller: SellerOut
