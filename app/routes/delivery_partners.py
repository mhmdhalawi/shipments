from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from services.delivery_partner import DeliveryPartnerDep, CurrentDeliveryPartnerDep, Token
from validation import DeliveryPartnerCreate, DeliveryPartnerLocationCreate


router = APIRouter(
    prefix="/partner",
    tags=["Delivery Partner"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_partner(partner: DeliveryPartnerCreate, service: DeliveryPartnerDep):
    return await service.create(partner)


@router.post("/login")
async def login_partner(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()], service: DeliveryPartnerDep
):
    return await service.login(credentials.username, credentials.password)


@router.get("/me")
async def get_current_partner(partner: CurrentDeliveryPartnerDep):
    return partner


@router.post("/logout")
async def logout_partner(token: Token, service: DeliveryPartnerDep):
    await service.logout(token)
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(token: Token, service: DeliveryPartnerDep):
    return await service.refresh(token)


@router.post("/me/locations", status_code=status.HTTP_201_CREATED)
async def add_location(
    location: DeliveryPartnerLocationCreate,
    partner: CurrentDeliveryPartnerDep,
    service: DeliveryPartnerDep,
):
    return await service.add_location(partner.id, location)


@router.delete("/me/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_location(
    location_id: UUID,
    partner: CurrentDeliveryPartnerDep,
    service: DeliveryPartnerDep,
):
    await service.remove_location(partner.id, location_id)
