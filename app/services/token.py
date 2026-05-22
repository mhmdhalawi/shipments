import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis

from config import settings


@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> Redis:
    return get_redis_client()


RedisDep = Annotated[Redis, Depends(get_redis)]


class TokenService:
    def __init__(self, redis: Redis):
        self.redis = redis

    def create_access_token(self, data: dict[str, Any]) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
        payload["jti"] = str(uuid.uuid4())
        payload["type"] = "access"
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
        payload["jti"] = str(uuid.uuid4())
        payload["type"] = "refresh"
        return jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm="HS256")

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return payload

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token, settings.REFRESH_SECRET_KEY, algorithms=["HS256"]
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return payload

    async def is_blacklisted(self, jti: str) -> bool:
        return bool(await self.redis.exists(f"blacklist:{jti}"))

    async def blacklist_token(self, payload: dict[str, Any]) -> None:
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or exp is None:
            return

        ttl = exp - int(datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            await self.redis.setex(f"blacklist:{jti}", ttl, "1")


def get_token_service(redis: RedisDep) -> TokenService:
    return TokenService(redis)


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
