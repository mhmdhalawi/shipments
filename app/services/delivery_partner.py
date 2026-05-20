import jwt
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from sqlite3 import IntegrityError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from database import SessionDep
from validation import DeliveryPartnerCreate, DeliveryPartnerLocationCreate
from models import DeliveryPartner, DeliveryPartnerLocation
from config import settings
from services.user import UserService, redis


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/partner/login")


class DeliveryPartnerService:
    def __init__(self, session):
        self.session = session
        self.auth = UserService(session, DeliveryPartner, "partner")

    async def create(self, partner: DeliveryPartnerCreate) -> dict:
        db_partner = DeliveryPartner(
            name=partner.name,
            email=partner.email,
            password_hash=self.auth.hash_password(partner.password),
            service_radius_km=partner.service_radius_km,
            max_handling_capacity=partner.max_handling_capacity,
        )
        self.session.add(db_partner)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        return self.auth.build_token_response(db_partner)

    async def login(self, username: str, password: str) -> dict:
        return await self.auth.login(username, password)

    async def logout(self, token: str):
        return await self.auth.logout(token)

    async def refresh(self, refresh_token: str) -> dict:
        return await self.auth.refresh(refresh_token)

    async def add_location(
        self, partner_id: UUID, location_data: DeliveryPartnerLocationCreate
    ) -> DeliveryPartnerLocation:
        point = from_shape(Point(location_data.longitude, location_data.latitude), srid=4326)
        db_location = DeliveryPartnerLocation(
            delivery_partner_id=partner_id,
            location=point,
            label=location_data.label,
        )
        self.session.add(db_location)
        await self.session.commit()
        await self.session.refresh(db_location)
        return db_location

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

        await self.session.delete(location)
        await self.session.commit()


def get_delivery_partner_service(session: SessionDep) -> DeliveryPartnerService:
    return DeliveryPartnerService(session)


async def get_current_delivery_partner(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> DeliveryPartner:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        partner_id = payload.get("sub")
        jti = payload.get("jti")

        if not partner_id or not jti:
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

    partner = await session.get(DeliveryPartner, UUID(partner_id))
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Delivery partner not found",
        )

    return partner


Token = Annotated[str, Depends(oauth2_scheme)]

DeliveryPartnerDep = Annotated[DeliveryPartnerService, Depends(get_delivery_partner_service)]
CurrentDeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_delivery_partner)]
