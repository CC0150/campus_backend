from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success_response
from app.schemas.shop import ShopSchema, ShopDetailSchema
from app.services import shop_service

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("")
def get_shops(db: Session = Depends(get_db)):
    shops = shop_service.get_shops(db)
    return success_response(
        data=[ShopSchema.model_validate(s).model_dump() for s in shops]
    )


@router.get("/{shop_id}")
def get_shop(shop_id: str, db: Session = Depends(get_db)):
    shop = shop_service.get_shop_detail(db, shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail="商家不存在")
    return success_response(
        data=ShopDetailSchema.model_validate(shop).model_dump()
    )
