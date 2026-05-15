from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from validation import SellerResponse
from services import SellerDep, CurrentSellerDep, Token
from validation import SellerCreate


router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.post(
    "/register", response_model=SellerResponse, status_code=status.HTTP_201_CREATED
)
async def register_seller(seller: SellerCreate, service: SellerDep):
    db_seller = await service.create(seller)
    return db_seller


@router.post("/login")
async def login_seller(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()], service: SellerDep
):
    return await service.login(credentials.username, credentials.password)


@router.get("/me")
async def get_current_seller(seller: CurrentSellerDep):
    return seller


@router.post("/logout")
async def logout_seller(token: Token, service: SellerDep):
    await service.logout(token)
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(token: Token, service: SellerDep):
    return await service.refresh(token)
