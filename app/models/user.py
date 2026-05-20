from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from utils import generate_uuid7


class User(SQLModel):
    id: UUID = Field(default_factory=generate_uuid7)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
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
