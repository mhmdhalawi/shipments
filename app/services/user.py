import bcrypt
from uuid import UUID
from typing import Generic, TypeVar
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.user import User
from services.base import BaseService
from services.token import TokenService


UserT = TypeVar("UserT", bound=User)


class UserService(BaseService[UserT], Generic[UserT]):
    def __init__(
        self,
        session: AsyncSession,
        token_service: TokenService,
        model_class: type[UserT],
        response_key: str,
    ):
        super().__init__(model_class, session)
        self.token_service = token_service
        self.model_class = model_class
        self.response_key = response_key

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def build_token_response(self, user: UserT) -> dict:
        data = {"sub": str(user.id), "email": user.email}
        return {
            "access_token": self.token_service.create_access_token(data),
            "refresh_token": self.token_service.create_refresh_token(data),
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
        payload = self.token_service.decode_access_token(token)
        await self.token_service.blacklist_token(payload)

    async def get_current_user(self, token: str) -> UserT:
        payload = self.token_service.decode_access_token(token)
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if await self.token_service.is_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        user = await self.session.get(self.model_class, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{self.model_class.__name__} not found",
            )

        return user

    async def refresh(self, refresh_token: str) -> dict:
        payload = self.token_service.decode_refresh_token(refresh_token)
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if await self.token_service.is_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        user = await self.session.get(self.model_class, UUID(payload["sub"]))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{self.model_class.__name__} not found",
            )

        await self.token_service.blacklist_token(payload)

        return self.build_token_response(user)
