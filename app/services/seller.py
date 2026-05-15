import uuid
import jwt
import bcrypt
from uuid import UUID
from redis.asyncio import Redis
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
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def _create_access_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
        payload["jti"] = str(uuid.uuid4())
        payload["type"] = "access"
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def _create_refresh_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
        payload["jti"] = str(uuid.uuid4())
        payload["type"] = "refresh"
        return jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm="HS256")

    def _build_token_response(self, seller: Seller) -> dict:
        data = {"sub": str(seller.id), "email": seller.email}
        return {
            "access_token": self._create_access_token(data),
            "refresh_token": self._create_refresh_token(data),
            "token_type": "bearer",
            "seller": SellerResponse.model_validate(seller),
        }

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

        return self._build_token_response(db_seller)

    async def login(self, username: str, password: str) -> dict:
        result = await self.session.exec(select(Seller).where(Seller.email == username))
        seller = result.first()

        if not seller or not self._verify_password(password, seller.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return self._build_token_response(seller)

    async def logout(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            exp = payload.get("exp")

            if jti and exp:
                # TTL = remaining lifetime of the token
                ttl = exp - int(datetime.now(timezone.utc).timestamp())
                if ttl > 0:
                    await redis.setex(f"blacklist:{jti}", ttl, "1")

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    async def refresh(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_SECRET_KEY, algorithms=["HS256"]
            )

            # make sure it's actually a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            jti = payload.get("jti")
            if not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            # check blacklist
            if await redis.exists(f"blacklist:{jti}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        seller = await self.session.get(Seller, UUID(payload["sub"]))
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Seller not found"
            )

        # blacklist the used refresh token (rotation — each refresh token is one-use)
        exp = payload.get("exp")
        if exp is not None:
            ttl = exp - int(datetime.now(timezone.utc).timestamp())
            if ttl > 0:
                await redis.setex(f"blacklist:{jti}", ttl, "1")

        # issue a fresh pair
        return self._build_token_response(seller)


# Dependency Injection
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
        # Check blacklist
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
