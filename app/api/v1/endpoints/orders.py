from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import success_response
from app.schemas.order import OrderCreateSchema, OrderSchema
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


class StatusUpdateBody(BaseModel):
    status: str


@router.post("")
def create_order(
    body: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 鉴权：防止越权下单
):
    """创建订单 — 从 JWT 令牌获取用户身份，扣减余额并生成订单记录"""
    try:
        order = order_service.create_order(db, body, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return success_response(
        data=OrderSchema.model_validate(order).model_dump(),
        msg="订单创建成功",
    )


@router.get("")
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 鉴权：只返回当前用户的订单
):
    """获取当前用户的订单历史列表"""
    orders = order_service.get_orders(db, current_user.student_id)
    return success_response(
        data=[OrderSchema.model_validate(o).model_dump() for o in orders]
    )


@router.put("/{order_id}/status")
def update_order_status(
    order_id: str,
    body: StatusUpdateBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新订单状态（支付、确认收货等）"""
    try:
        order = order_service.update_order_status(db, order_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return success_response(
        data=OrderSchema.model_validate(order).model_dump(),
        msg="订单状态已更新",
    )
