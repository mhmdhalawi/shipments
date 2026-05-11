from sqlmodel import SQLModel, Field
from utils import generate_uuid7
from pydantic import EmailStr


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"  # type: ignore
    id: int | None = Field(default_factory=generate_uuid7, primary_key=True)
    name: str = Field(min_length=1, max_length=100, description="Name of the seller")
    email: EmailStr = Field(
        min_length=5,
        max_length=100,
        description="Email address of the seller",
    )
    password_hash: str = Field(
        min_length=60,
        description="Hashed password of the seller (bcrypt hash)",
    )
