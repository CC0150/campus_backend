from datetime import datetime
import random

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreateSchema


def _generate_order_id() -> str:
    now = datetime.now()
    seq = random.randint(0, 9999)
    return f"ORD{now.strftime('%Y%m%d%H%M')}{seq:04d}"


def create_order(db: Session, data: OrderCreateSchema, user: User) -> Order:
    """创建订单并扣减余额

    参数:
        db: 数据库会话
        data: 订单数据（商品、金额、就餐方式等）
        user: 当前登录用户（由 JWT 鉴权注入，防止越权）

    返回:
        已持久化的 Order 模型实例

    异常:
        ValueError — 余额不足
    """
    if user.balance < data.totalPrice:
        raise ValueError("余额不足")

    # 扣减余额
    user.balance -= data.totalPrice

    order = Order(
        id=_generate_order_id(),
        student_id=user.student_id,  # 从鉴权获取，不可伪造
        shop_name=data.shopName,
        items=[item.model_dump() for item in data.items],
        total_price=data.totalPrice,
        status="pending_pay",
        dining_type=data.diningType,
        pickup_time=data.pickupTime,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders(db: Session, student_id: str, skip: int = 0, limit: int = 50) -> list[Order]:
    """获取当前用户的订单历史（按时间倒序）"""
    return (
        db.query(Order)
        .filter(Order.student_id == student_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


VALID_STATUSES = {"pending_pay", "pending_accept", "delivering", "completed", "cancelled"}


def update_order_status(db: Session, order_id: str, status: str) -> Order | None:
    if status not in VALID_STATUSES:
        raise ValueError(f"无效的订单状态: {status}")
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        return None
    order.status = status
    db.commit()
    db.refresh(order)
    return order
