import bcrypt
from typing import Annotated
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import SessionDep
from validation import SellerCreate, SellerResponse
from models import Seller


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, seller: SellerCreate) -> SellerResponse:
        existing = await self.session.exec(
            select(Seller).where(Seller.email == seller.email)
        )
        if existing.first():
            raise ValueError("Email already registered")

        password_hash = bcrypt.hashpw(
            seller.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        db_seller = Seller(
            name=seller.name,
            email=seller.email,
            password_hash=password_hash,
        )
        self.session.add(db_seller)
        await self.session.commit()
        return SellerResponse.model_validate(db_seller)


def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)


SellerDep = Annotated[SellerService, Depends(get_seller_service)]
