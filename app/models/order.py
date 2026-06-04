from datetime import datetime

from sqlalchemy import Column, String, Float, JSON, ForeignKey

from app.models import Base


class Order(Base):
    """订单模型 — 记录每笔交易的核心信息"""

    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    # 关联下单用户（外键指向 users.student_id）
    student_id = Column(String, ForeignKey("users.student_id"), nullable=False)
    shop_name = Column(String, nullable=False)
    items = Column(JSON, nullable=False)          # 商品明细 [{id, name, quantity, price}]
    total_price = Column(Float, nullable=False)   # 实付金额（含配送费）
    status = Column(String, default="pending_pay") # pending_pay | delivering | completed | cancelled
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    dining_type = Column(String, default="堂食")   # 堂食 / 打包
    pickup_time = Column(String, default="")       # 预计取餐时间
