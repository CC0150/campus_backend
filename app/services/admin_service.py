from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order
from app.models.shop import Shop
from app.models.dish import Dish
from app.models.user import User
from app.core.security import get_password_hash


def get_dashboard_stats(db: Session, date: str | None = None) -> dict:
    """获取仪表盘统计数据。
    date 为可选筛选日期（格式 YYYY-MM-DD），传入时仅统计该日数据；
    不传时统计全部历史数据。
    """
    # 基础查询 — 可按日期过滤
    order_q = db.query(Order)
    revenue_q = db.query(func.coalesce(func.sum(Order.total_price), 0))
    if date:
        order_q = order_q.filter(Order.created_at.like(f'{date}%'))
        revenue_q = revenue_q.filter(Order.created_at.like(f'{date}%'))

    total_orders = order_q.count()
    total_revenue = revenue_q.filter(Order.status == 'completed').scalar()

    total_shops = db.query(Shop).count()
    total_dishes = db.query(Dish).count()

    statuses = ['pending_pay', 'pending_accept', 'delivering', 'completed', 'cancelled']
    labels = ['待支付', '待接单', '配送中', '已完成', '已取消']
    status_distribution = []
    for status, label in zip(statuses, labels):
        q = db.query(Order).filter(Order.status == status)
        if date:
            q = q.filter(Order.created_at.like(f'{date}%'))
        count = q.count()
        status_distribution.append({"status": status, "count": count, "label": label})

    # last_7_days — 以筛选日期或今天为结束日，向前推 6 天
    ref_date = datetime.strptime(date, '%Y-%m-%d') if date else datetime.now()
    day_labels = ['一', '二', '三', '四', '五', '六', '日']
    last_7_days = []
    for i in range(6, -1, -1):
        d = ref_date - timedelta(days=i)
        date_str = d.strftime('%Y-%m-%d')
        day_label = day_labels[d.weekday()]

        day_orders = db.query(Order).filter(
            Order.created_at.like(f'{date_str}%')
        ).count()

        day_revenue = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
            Order.created_at.like(f'{date_str}%'),
            Order.status == 'completed'
        ).scalar()

        last_7_days.append({
            "date": date_str,
            "dayLabel": day_label,
            "orderCount": day_orders,
            "revenue": float(day_revenue)
        })

    return {
        "totalRevenue": float(total_revenue),
        "totalOrders": total_orders,
        "totalShops": total_shops,
        "totalDishes": total_dishes,
        "orderStatusDistribution": status_distribution,
        "last7Days": last_7_days
    }


def get_all_orders(db: Session, status: str | None = None):
    query = db.query(Order).order_by(Order.created_at.desc())
    if status:
        query = query.filter(Order.status == status)
    return query.all()


def get_all_dishes(db: Session, keyword: str | None = None, category: str | None = None):
    query = db.query(Dish)
    if keyword:
        query = query.filter(Dish.name.contains(keyword))
    if category:
        query = query.filter(Dish.category == category)
    return query.all()


def create_dish(db: Session, data) -> Dish:
    dish = Dish(
        id=data.id if hasattr(data, 'id') and data.id else _gen_dish_id(),
        name=data.name,
        price=data.price,
        image=data.image,
        category=data.category,
        sales=0,
        shop_id=data.shop_id,
    )
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


def update_dish(db: Session, dish_id: str, data) -> Dish | None:
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dish, key, value)
    db.commit()
    db.refresh(dish)
    return dish


def delete_dish(db: Session, dish_id: str) -> bool:
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        return False
    db.delete(dish)
    db.commit()
    return True


def get_all_shops(db: Session, keyword: str | None = None):
    query = db.query(Shop)
    if keyword:
        query = query.filter(
            (Shop.name.contains(keyword)) | (Shop.id.contains(keyword))
        )
    return query.order_by(Shop.sales.desc()).all()


def get_all_users(db: Session, keyword: str | None = None):
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.student_id.contains(keyword)) | (User.name.contains(keyword))
        )
    return query.order_by(User.student_id).all()


def create_shop(db: Session, data) -> Shop:
    shop = Shop(
        id=data.id,
        name=data.name,
        rating=data.rating,
        sales=0,
        min_order=data.min_order,
        delivery_fee=data.delivery_fee,
        delivery_time=data.delivery_time,
        notice=data.notice,
        image=data.image,
        tags=data.tags,
        discount=data.discount,
        bulletin=data.bulletin,
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def update_shop(db: Session, shop_id: str, data) -> Shop | None:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shop, key, value)
    db.commit()
    db.refresh(shop)
    return shop


def delete_shop(db: Session, shop_id: str) -> bool:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        return False
    # Also delete dishes belonging to this shop
    db.query(Dish).filter(Dish.shop_id == shop_id).delete()
    db.delete(shop)
    db.commit()
    return True


def create_user(db: Session, data) -> User:
    user = User(
        student_id=data.student_id,
        name=data.name,
        password_hash=get_password_hash(data.password),
        balance=data.balance,
        avatar=data.avatar,
        addresses=data.addresses,
        security_question=data.security_question,
        security_answer=data.security_answer,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, student_id: str, data) -> User | None:
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            user.password_hash = get_password_hash(value)
        else:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, student_id: str) -> bool:
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        return False
    # Prevent deleting the admin account
    if student_id == "admin":
        return False
    db.delete(user)
    db.commit()
    return True


def _gen_dish_id() -> str:
    import random
    return f"D{random.randint(10000, 99999)}"
