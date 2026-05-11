from fastapi import APIRouter

from services import SellerDep
from validation import SellerCreate


router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.post("/register")
async def register_seller(seller: SellerCreate, service: SellerDep):
    await service.register_seller(seller)
    return {"message": "Seller registered successfully"}
