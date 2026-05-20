from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from services import SellerDep, Token, CurrentSellerDep
from validation import SellerCreate


router = APIRouter(
    prefix="/partner",
    tags=["Delivery Partner"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_partner(seller: SellerCreate, service: SellerDep):
    db_seller = await service.create(seller)
    return db_seller


@router.post("/login")
async def login_partner(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()], service: SellerDep
):
    return await service.login(credentials.username, credentials.password)


@router.get("/me")
async def get_current_partner(partner: CurrentSellerDep):
    return partner


@router.post("/logout")
async def logout_partner(token: Token, service: SellerDep):
    await service.logout(token)
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(token: Token, service: SellerDep):
    return await service.refresh(token)
