from fastapi.security import OAuth2PasswordBearer
from sqlite3 import IntegrityError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from database import SessionDep
from validation import SellerCreate
from models import Seller
from services.user import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sellers/login")

Token = Annotated[str, Depends(oauth2_scheme)]


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

    async def get_current_seller(self, token: str) -> Seller:
        return await self.auth.get_current_user(token)


def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)


SellerDep = Annotated[SellerService, Depends(get_seller_service)]


async def get_current_seller(
    token: Token,
    service: SellerDep,
) -> Seller:
    return await service.get_current_seller(token)


CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]
