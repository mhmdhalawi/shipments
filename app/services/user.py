import uuid
import jwt
import bcrypt
from uuid import UUID
from redis.asyncio import Redis
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Annotated, Generic, TypeVar
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.user import User
from config import settings
from services.base import BaseService


UserT = TypeVar("UserT", bound=User)


@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> Redis:
    return get_redis_client()


RedisDep = Annotated[Redis, Depends(get_redis)]


class UserService(BaseService[UserT], Generic[UserT]):
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        model_class: type[UserT],
        response_key: str,
    ):
        super().__init__(model_class, session)
        self.redis = redis
        self.model_class = model_class
        self.response_key = response_key

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def create_access_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
        payload["jti"] = str(uuid.uuid4())
        payload["type"] = "access"
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def create_refresh_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
        payload["jti"] = str(uuid.uuid4())
        payload["type"] = "refresh"
        return jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm="HS256")

    def build_token_response(self, user: UserT) -> dict:
        data = {"sub": str(user.id), "email": user.email}
        return {
            "access_token": self.create_access_token(data),
            "refresh_token": self.create_refresh_token(data),
            "token_type": "bearer",
            self.response_key: user,
        }

    async def get_by_email(self, email: str) -> UserT | None:
        result = await self.session.exec(
            select(self.model_class).where(self.model_class.email == email)
        )
        return result.first()

    async def login(self, username: str, password: str) -> dict:
        user = await self.get_by_email(username)

        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return self.build_token_response(user)

    async def logout(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            exp = payload.get("exp")

            if jti and exp:
                ttl = exp - int(datetime.now(timezone.utc).timestamp())
                if ttl > 0:
                    await self.redis.setex(f"blacklist:{jti}", ttl, "1")

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    async def get_current_user(self, token: str) -> UserT:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            jti = payload.get("jti")

            if not user_id or not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            if await self.redis.exists(f"blacklist:{jti}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = await self.session.get(self.model_class, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{self.model_class.__name__} not found",
            )

        return user

    async def refresh(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_SECRET_KEY, algorithms=["HS256"]
            )

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

            if await self.redis.exists(f"blacklist:{jti}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = await self.session.get(self.model_class, UUID(payload["sub"]))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{self.model_class.__name__} not found",
            )

        exp = payload.get("exp")
        if exp is not None:
            ttl = exp - int(datetime.now(timezone.utc).timestamp())
            if ttl > 0:
                await self.redis.setex(f"blacklist:{jti}", ttl, "1")

        return self.build_token_response(user)
