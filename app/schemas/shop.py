from pydantic import BaseModel, Field, ConfigDict

from .dish import DishSchema


class ShopSchema(BaseModel):
    id: str
    name: str
    rating: float
    sales: int
    minOrder: float = Field(alias="min_order")
    deliveryFee: float = Field(alias="delivery_fee")
    deliveryTime: int = Field(alias="delivery_time")
    notice: str
    image: str = "🍽️"
    tags: list[str] | None = None
    discount: str | None = None
    bulletin: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ShopDetailSchema(ShopSchema):
    dishes: list[DishSchema] = []
