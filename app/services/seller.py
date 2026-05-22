from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from database import SessionDep
from validation import SellerCreate, SellerOut
from models import Seller
from services.token import TokenService, TokenServiceDep
from services.user import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sellers/login")

Token = Annotated[str, Depends(oauth2_scheme)]


class SellerService(UserService[Seller]):
    def __init__(self, session: AsyncSession, token_service: TokenService):
        super().__init__(session, token_service, Seller, "seller")

    async def create(self, seller: SellerCreate) -> dict:
        seller_data = seller.model_dump(exclude={"password"})
        seller_data["password_hash"] = self.hash_password(seller.password)

        db_seller = Seller.model_validate(seller_data)
        self.session.add(db_seller)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        return self.build_token_response(db_seller)

    def build_token_response(self, user: Seller) -> dict:
        base = super().build_token_response(user)
        base["seller"] = SellerOut.model_validate(user)
        return base

    async def get_current_seller(self, token: str) -> Seller:
        return await self.get_current_user(token)


def get_seller_service(
    session: SessionDep, token_service: TokenServiceDep
) -> SellerService:
    return SellerService(session, token_service)


SellerDep = Annotated[SellerService, Depends(get_seller_service)]


async def get_current_seller(
    token: Token,
    service: SellerDep,
) -> Seller:
    return await service.get_current_seller(token)


CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]
