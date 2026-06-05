import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.schemas.common import success_response
from app.schemas.admin import DashboardStats, OrderStatusCount, DailyStats, DishCreate, DishUpdate, ShopCreate, ShopUpdate, UserCreate, UserUpdate
from app.schemas.dish import DishSchema
from app.schemas.shop import ShopSchema
from app.schemas.user import UserResponse
from app.schemas.order import OrderSchema
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    date: str | None = Query(default=None, description="筛选日期 (YYYY-MM-DD)，不传则统计全部"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """获取仪表盘统计数据，可按日期筛选"""
    stats = admin_service.get_dashboard_stats(db, date=date)
    return success_response(data=stats)


@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user),
):
    """上传图片，返回访问 URL"""
    # 仅允许图片类型
    allowed = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="仅支持 PNG/JPG/GIF/WebP/SVG 格式")

    ext = os.path.splitext(file.filename or ".png")[1] or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"

    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    url = f"/uploads/{filename}"
    return success_response(data=url, msg="上传成功")


@router.get("/orders")
def get_orders(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """获取全部订单列表（不受用户范围限制）"""
    orders = admin_service.get_all_orders(db, status)
    return success_response(
        data=[OrderSchema.model_validate(o).model_dump() for o in orders]
    )


@router.get("/dishes")
def get_dishes(
    keyword: str | None = Query(None),
    category: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """获取全部菜品列表"""
    dishes = admin_service.get_all_dishes(db, keyword, category)
    return success_response(
        data=[DishSchema.model_validate(d).model_dump() for d in dishes]
    )


@router.post("/dishes")
def create_dish(
    body: DishCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """新增菜品"""
    dish = admin_service.create_dish(db, body)
    return success_response(
        data=DishSchema.model_validate(dish).model_dump(),
        msg="菜品创建成功"
    )


@router.put("/dishes/{dish_id}")
def update_dish(
    dish_id: str,
    body: DishUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """更新菜品"""
    dish = admin_service.update_dish(db, dish_id, body)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return success_response(
        data=DishSchema.model_validate(dish).model_dump(),
        msg="菜品更新成功"
    )


@router.delete("/dishes/{dish_id}")
def delete_dish(
    dish_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """删除菜品"""
    ok = admin_service.delete_dish(db, dish_id)
    if not ok:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return success_response(msg="菜品已删除")


@router.get("/users")
def get_users(
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """获取全部用户列表，支持按学号 / 姓名搜索"""
    users = admin_service.get_all_users(db, keyword)
    return success_response(
        data=[UserResponse.model_validate(u).model_dump(by_alias=True) for u in users]
    )


@router.post("/users")
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """新增用户（管理员创建学生账号）"""
    existing = db.query(User).filter(User.student_id == body.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该用户 ID 已存在")
    user = admin_service.create_user(db, body)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(by_alias=True),
        msg="用户创建成功"
    )


@router.put("/users/{student_id}")
def update_user(
    student_id: str,
    body: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """更新用户信息"""
    user = admin_service.update_user(db, student_id, body)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return success_response(
        data=UserResponse.model_validate(user).model_dump(by_alias=True),
        msg="用户更新成功"
    )


@router.delete("/users/{student_id}")
def delete_user(
    student_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """删除用户（禁止删除 admin 账号）"""
    ok = admin_service.delete_user(db, student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="用户不存在或禁止操作")
    return success_response(msg="用户已删除")


@router.get("/shops")
def get_shops(
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """获取全部商家列表（含销量数据），支持按名称 / ID 搜索"""
    shops = admin_service.get_all_shops(db, keyword)
    return success_response(
        data=[ShopSchema.model_validate(s).model_dump() for s in shops]
    )


@router.post("/shops")
def create_shop(
    body: ShopCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """新增商家"""
    shop = admin_service.create_shop(db, body)
    return success_response(
        data=ShopSchema.model_validate(shop).model_dump(),
        msg="商家创建成功"
    )


@router.put("/shops/{shop_id}")
def update_shop(
    shop_id: str,
    body: ShopUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """更新商家信息"""
    shop = admin_service.update_shop(db, shop_id, body)
    if not shop:
        raise HTTPException(status_code=404, detail="商家不存在")
    return success_response(
        data=ShopSchema.model_validate(shop).model_dump(),
        msg="商家更新成功"
    )


@router.delete("/shops/{shop_id}")
def delete_shop(
    shop_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """删除商家（同时删除旗下菜品）"""
    ok = admin_service.delete_shop(db, shop_id)
    if not ok:
        raise HTTPException(status_code=404, detail="商家不存在")
    return success_response(msg="商家已删除")
