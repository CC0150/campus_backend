from pydantic import BaseModel, Field, ConfigDict


class OrderItemSchema(BaseModel):
    id: str
    name: str
    quantity: int
    price: float


class OrderSchema(BaseModel):
    id: str
    shopName: str = Field(alias="shop_name")
    items: list[OrderItemSchema]
    totalPrice: float = Field(alias="total_price")
    status: str
    createdAt: str = Field(alias="created_at")
    diningType: str = Field(alias="dining_type")
    pickupTime: str = Field(alias="pickup_time")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OrderCreateSchema(BaseModel):
    """下单请求体 — 用户身份由 JWT 令牌提供，不在此处传入"""
    shopName: str
    items: list[OrderItemSchema]
    totalPrice: float
    diningType: str = "堂食"
    pickupTime: str = ""
