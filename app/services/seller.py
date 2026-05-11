import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import SessionDep
from validation import SellerCreate, SellerLogin, SellerResponse
from models import Seller
from config import settings


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    async def create(self, seller: SellerCreate) -> Seller:
        existing = await self.session.exec(
            select(Seller).where(Seller.email == seller.email)
        )
        if existing.first():
            raise ValueError("Email already registered")

        db_seller = Seller(
            name=seller.name,
            email=seller.email,
            password_hash=self._hash_password(seller.password),
        )
        self.session.add(db_seller)
        await self.session.commit()
        return db_seller

    async def login(self, credentials: SellerLogin) -> dict:
        result = await self.session.exec(
            select(Seller).where(Seller.email == credentials.email)
        )
        seller = result.first()

        if not seller or not self._verify_password(
            credentials.password, seller.password_hash
        ):
            raise ValueError("Invalid email or password")

        token = self._create_access_token(
            {"sub": str(seller.id), "email": seller.email}
        )
        return {
            "access_token": token,
            "seller": SellerResponse.model_validate(seller),
        }

    def _create_access_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
        return jwt.encode(payload, settings.SECRET_KEY)


def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)


SellerDep = Annotated[SellerService, Depends(get_seller_service)]
