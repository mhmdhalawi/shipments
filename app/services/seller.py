import jwt
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from sqlite3 import IntegrityError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from database import SessionDep
from validation import SellerCreate
from models import Seller
from config import settings
from services.user import UserService, redis


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sellers/login")


class SellerService:
    def __init__(self, session):
        self.session = session
        self.auth = UserService(session, Seller, "seller")

    async def create(self, seller: SellerCreate) -> dict:
        db_seller = Seller(
            name=seller.name,
            email=seller.email,
            password_hash=self.auth.hash_password(seller.password),
        )
        self.session.add(db_seller)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        return self.auth.build_token_response(db_seller)

    async def login(self, username: str, password: str) -> dict:
        return await self.auth.login(username, password)

    async def logout(self, token: str):
        return await self.auth.logout(token)

    async def refresh(self, refresh_token: str) -> dict:
        return await self.auth.refresh(refresh_token)


def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)


async def get_current_seller(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> Seller:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        seller_id = payload.get("sub")
        jti = payload.get("jti")

        if not seller_id or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if await redis.exists(f"blacklist:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
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


Token = Annotated[str, Depends(oauth2_scheme)]

CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]

SellerDep = Annotated[SellerService, Depends(get_seller_service)]
