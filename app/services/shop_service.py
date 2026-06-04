from sqlalchemy.orm import Session, joinedload

from app.models.shop import Shop


def get_shops(db: Session, skip: int = 0, limit: int = 20) -> list[Shop]:
    return db.query(Shop).offset(skip).limit(limit).all()


def get_shop_detail(db: Session, shop_id: str) -> Shop | None:
    return (
        db.query(Shop)
        .options(joinedload(Shop.dishes))
        .filter(Shop.id == shop_id)
        .first()
    )
