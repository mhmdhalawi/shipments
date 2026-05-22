from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from database import SessionDep
from validation import (
    DeliveryPartnerCreate,
    DeliveryPartnerLocationCreate,
    DeliveryPartnerOut,
)
from models import DeliveryPartner, DeliveryPartnerLocation
from services.user import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/partners/login")

Token = Annotated[str, Depends(oauth2_scheme)]


class DeliveryPartnerService(UserService[DeliveryPartner]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DeliveryPartner, "partner")

    async def create(self, partner: DeliveryPartnerCreate) -> dict:
        partner_data = partner.model_dump(exclude={"password"})
        partner_data["password_hash"] = self.hash_password(partner.password)

        db_partner = DeliveryPartner.model_validate(partner_data)
        self.session.add(db_partner)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        return self.build_token_response(db_partner)

    def build_token_response(self, user: DeliveryPartner) -> dict:
        base = super().build_token_response(user)
        base["partner"] = DeliveryPartnerOut.model_validate(user)
        return base

    async def add_location(
        self, partner_id: UUID, location_data: DeliveryPartnerLocationCreate
    ) -> DeliveryPartnerLocation:
        point = from_shape(
            Point(location_data.longitude, location_data.latitude), srid=4326
        )
        db_location = DeliveryPartnerLocation(
            delivery_partner_id=partner_id,
            location=point,
            label=location_data.label,
        )
        return await self._add(db_location)

    async def remove_location(self, partner_id: UUID, location_id: UUID):
        result = await self.session.exec(
            select(DeliveryPartnerLocation).where(
                DeliveryPartnerLocation.id == location_id,
                DeliveryPartnerLocation.delivery_partner_id == partner_id,
            )
        )
        location = result.first()

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        await self._delete(location)

    async def get_current_partner(self, token: str) -> DeliveryPartner:
        user = await self.get_current_user(token)
        result = await self.session.exec(
            select(DeliveryPartner).where(DeliveryPartner.id == user.id)
        )
        partner = result.first()
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found"
            )
        return partner


def get_delivery_partner_service(session: SessionDep) -> DeliveryPartnerService:
    return DeliveryPartnerService(session)


DeliveryPartnerDep = Annotated[
    DeliveryPartnerService, Depends(get_delivery_partner_service)
]


async def get_current_delivery_partner(
    token: Token,
    service: DeliveryPartnerDep,
) -> DeliveryPartner:
    return await service.get_current_partner(token)


CurrentDeliveryPartnerDep = Annotated[
    DeliveryPartner, Depends(get_current_delivery_partner)
]
