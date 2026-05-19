from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class User(SQLModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Name of the seller",
    )
    email: EmailStr = Field(
        min_length=5,
        max_length=100,
        unique=True,
        description="Email address of the seller",
    )
    password_hash: str = Field(
        min_length=60,
        description="Hashed password of the seller (bcrypt hash)",
        exclude=True,
    )
