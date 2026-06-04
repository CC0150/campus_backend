"""
鉴权接口 — 登录 / 登出 / 获取当前用户

路由前缀: /api/v1（由 main.py 中 include_router 统一添加）

接口列表:
- POST /login         —— 学号 + 密码登录，返回 JWT
- POST /logout        —— 退出登录（验证令牌）
- GET  /users/me      —— 获取当前登录用户信息
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserLogin, UserRegister, Token, TopUpBody, UpdateAddressBody,
    ForgotPasswordCheck, ForgotPasswordVerify, ForgotPasswordReset,
    UpdatePasswordBody,
)
from app.schemas.common import success_response
from app.schemas.user import UserResponse
from app.services import auth_service
from app.core.security import get_password_hash, verify_password

router = APIRouter(tags=["auth"])


@router.post("/register")
def register(body: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口

    请求体:
        { "studentId": "2023110402", "name": "李四", "password": "123456" }

    成功返回:
        { "code": 200, "data": null, "msg": "注册成功" }

    失败返回:
        HTTP 400 — 学号已被注册
    """
    try:
        auth_service.register_user(db, body.student_id, body.name, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return success_response(msg="注册成功，请登录")


@router.post("/login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口

    请求体:
        { "studentId": "123456", "password": "123456" }

    成功返回:
        { "code": 200, "data": { "access_token": "...", "token_type": "bearer" }, "msg": "登录成功" }

    失败返回:
        HTTP 400 — 学号或密码错误
    """
    # 调用认证服务：验证学号 + 密码，签发 JWT
    token = auth_service.authenticate_user(db, body.student_id, body.password)
    if token is None:
        raise HTTPException(status_code=400, detail="学号或密码错误")

    return success_response(
        data=Token(access_token=token).model_dump(),
        msg="登录成功",
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出接口

    需要携带有效的 Bearer 令牌。
    当前为无状态 JWT 方案，服务端不维护黑名单，
    前端清除本地令牌即可完成登出。
    """
    return success_response(msg="已退出登录")


@router.post("/forgot-password/check")
def forgot_password_check(body: ForgotPasswordCheck, db: Session = Depends(get_db)):
    """
    忘记密码 — 步骤1：检查学号是否存在，返回密保问题

    请求体:
        { "studentId": "2023110402" }

    成功返回密保问题；失败返回 404。
    """
    user = auth_service.get_user_by_student_id(db, body.student_id)
    if user is None:
        raise HTTPException(status_code=404, detail="该学号未在系统中注册")
    return success_response(
        data={"securityQuestion": user.security_question},
        msg="学号验证通过",
    )


@router.post("/forgot-password/verify")
def forgot_password_verify(body: ForgotPasswordVerify, db: Session = Depends(get_db)):
    """
    忘记密码 — 步骤2：验证密保答案

    请求体:
        { "studentId": "2023110402", "answer": "小白" }

    成功返回 msg；失败返回 400。
    """
    user = auth_service.get_user_by_student_id(db, body.student_id)
    if user is None:
        raise HTTPException(status_code=404, detail="该学号未在系统中注册")
    if user.security_answer != body.answer:
        raise HTTPException(status_code=400, detail="密保答案错误")
    return success_response(msg="密保验证通过")


@router.post("/forgot-password/reset")
def forgot_password_reset(body: ForgotPasswordReset, db: Session = Depends(get_db)):
    """
    忘记密码 — 步骤3：重置密码

    请求体:
        { "studentId": "2023110402", "newPassword": "newpass123" }

    成功后需重新登录。
    """
    user = auth_service.get_user_by_student_id(db, body.student_id)
    if user is None:
        raise HTTPException(status_code=404, detail="该学号未在系统中注册")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少需要 6 位字符")
    user.password_hash = get_password_hash(body.new_password)
    db.commit()
    return success_response(msg="密码重置成功，请使用新密码登录")


@router.put("/users/me/password")
def update_password(
    body: UpdatePasswordBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    修改密码接口（需登录）

    请求体:
        { "oldPassword": "123456", "newPassword": "newpass123" }

    验证旧密码后更新为新密码。
    """
    if not verify_password(body.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少需要 6 位字符")
    current_user.password_hash = get_password_hash(body.new_password)
    db.commit()
    return success_response(msg="密码修改成功")


@router.get("/users/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息

    返回字段包括 studentId、name、balance、avatar。
    字段名使用 camelCase（与前端约定一致）。
    """
    return success_response(
        data=UserResponse.model_validate(current_user).model_dump(by_alias=True)
    )


@router.put("/users/me/topup")
def topup_balance(
    body: TopUpBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    钱包充值接口

    请求体:
        { "amount": 50.0 }

    返回更新后的用户信息（含最新余额）。
    """
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于 0")
    if body.amount > 500:
        raise HTTPException(status_code=400, detail="单笔充值不可超过 500 元")

    # 直接在数据库会话中更新余额
    current_user.balance += body.amount
    db.commit()
    db.refresh(current_user)

    return success_response(
        data=UserResponse.model_validate(current_user).model_dump(by_alias=True),
        msg=f"成功充值 ¥{body.amount:.2f}",
    )


@router.put("/users/me/addresses")
def update_addresses(
    body: UpdateAddressBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    同步收货地址

    请求体:
        { "addresses": ["寝室1栋101", "图书馆2楼"], "activeAddressIndex": 0 }

    将地址列表和当前选中索引持久化到数据库。
    """
    if len(body.addresses) > 5:
        raise HTTPException(status_code=400, detail="最多只能添加 5 个收货地址")

    current_user.addresses = body.addresses
    current_user.active_address_index = body.activeAddressIndex
    db.commit()
    db.refresh(current_user)

    return success_response(
        data=UserResponse.model_validate(current_user).model_dump(by_alias=True),
        msg="地址已同步",
    )
