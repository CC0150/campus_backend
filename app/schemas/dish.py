from pydantic import BaseModel, ConfigDict


class DishSchema(BaseModel):
    id: str
    name: str
    price: float
    image: str
    category: str
    sales: int
    shop_id: str = ""

    model_config = ConfigDict(from_attributes=True)
