from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from validation import SellerResponse
from services import SellerDep, CurrentSellerDep
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
