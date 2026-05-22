from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from services import SellerDep, CurrentSellerDep, Token
from validation import SellerCreate, SellerOut


router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_seller(seller: SellerCreate, service: SellerDep):
    db_seller = await service.create(seller)
    return db_seller


@router.post("/login")
async def login_seller(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()], service: SellerDep
):
    return await service.login(credentials.username, credentials.password)


@router.get("/me", response_model=SellerOut)
async def get_current_seller(seller: CurrentSellerDep):
    return seller


@router.post("/logout")
async def logout_seller(token: Token, service: SellerDep):
    await service.logout(token)
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(token: Token, service: SellerDep):
    return await service.refresh(token)
