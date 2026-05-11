from fastapi import APIRouter

from validation import SellerResponse
from services import SellerDep
from validation import SellerCreate


router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.post("/register", response_model=SellerResponse)
async def register_seller(seller: SellerCreate, service: SellerDep):
    db_seller = await service.create(seller)
    return db_seller
