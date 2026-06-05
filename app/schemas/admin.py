from pydantic import BaseModel, Field


class OrderStatusCount(BaseModel):
    status: str
    count: int
    label: str


class DailyStats(BaseModel):
    date: str
    dayLabel: str
    orderCount: int
    revenue: float


class DashboardStats(BaseModel):
    totalRevenue: float
    totalOrders: int
    totalShops: int
    totalDishes: int
    orderStatusDistribution: list[OrderStatusCount]
    last7Days: list[DailyStats]


class DishCreate(BaseModel):
    name: str
    price: float
    image: str
    category: str
    shop_id: str


class DishUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    image: str | None = None
    category: str | None = None
    shop_id: str | None = None


class ShopCreate(BaseModel):
    id: str
    name: str
    rating: float = 5.0
    min_order: float = 0.0
    delivery_fee: float = 0.0
    delivery_time: int = 30
    notice: str = ""
    image: str = ""
    tags: list[str] = []
    discount: str | None = None
    bulletin: str | None = None


class ShopUpdate(BaseModel):
    name: str | None = None
    rating: float | None = None
    min_order: float | None = None
    delivery_fee: float | None = None
    delivery_time: int | None = None
    notice: str | None = None
    image: str | None = None
    tags: list[str] | None = None
    discount: str | None = None
    bulletin: str | None = None


class UserCreate(BaseModel):
    student_id: str = Field(alias="studentId")
    name: str
    password: str
    balance: float = 50.0
    avatar: str = "🧑‍🎓"
    addresses: list[str] = []
    security_question: str = Field(default="你的第一只宠物叫什么名字？", alias="securityQuestion")
    security_answer: str = Field(default="小白", alias="securityAnswer")


class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
    balance: float | None = None
    avatar: str | None = None
    addresses: list[str] | None = None
    active_address_index: int | None = Field(default=None, alias="activeAddressIndex")
    security_question: str | None = Field(default=None, alias="securityQuestion")
    security_answer: str | None = Field(default=None, alias="securityAnswer")
