import jwt
import bcrypt
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from sqlite3 import IntegrityError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import SessionDep
from validation import SellerCreate, SellerResponse
from models import Seller
from config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sellers/login")


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def _create_access_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
        return jwt.encode(payload, settings.SECRET_KEY)

    async def create(self, seller: SellerCreate) -> dict:
        db_seller = Seller(
            name=seller.name,
            email=seller.email,
            password_hash=self._hash_password(seller.password),
        )
        self.session.add(db_seller)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        token = self._create_access_token(
            {"sub": str(db_seller.id), "email": db_seller.email}
        )
        return {
            "access_token": token,
            "seller": SellerResponse.model_validate(db_seller),
        }

    async def login(self, username: str, password: str) -> dict:
        result = await self.session.exec(select(Seller).where(Seller.email == username))
        seller = result.first()

        if not seller or not self._verify_password(password, seller.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = self._create_access_token(
            {"sub": str(seller.id), "email": seller.email}
        )
        return {
            "access_token": token,
            "seller": SellerResponse.model_validate(seller),
        }


# Dependency Injection
def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)


async def get_current_seller(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> Seller:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        seller_id = payload.get("sub")
        if not seller_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    seller = await session.get(Seller, UUID(seller_id))
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Seller not found"
        )

    return seller


CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]

SellerDep = Annotated[SellerService, Depends(get_seller_service)]
