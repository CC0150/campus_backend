"""
认证依赖注入模块

提供 FastAPI 的 Depends 依赖项，用于：
1. Bearer 令牌提取与验证
2. 当前登录用户的注入

使用方式：
    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import get_user_by_student_id

# Bearer 令牌安全方案（从 Authorization 请求头提取令牌）
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    """
    从请求中提取并验证 JWT，返回当前登录用户

    验证链路：
    1. HTTPBearer 解析 Authorization: Bearer <token>
    2. 解码 JWT，提取 payload
    3. 从 payload.sub 获取学号
    4. 通过学号查询数据库获取 User 模型实例

    参数:
        credentials: HTTPBearer 自动提取的凭证对象
        db: 数据库会话

    返回:
        当前登录的 User 模型实例

    异常:
        HTTP 401 — 令牌无效、过期或用户不存在
    """
    # 解码 JWT 令牌
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

    # 提取学号
    student_id = payload.get("sub")
    if student_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

    # 查询用户
    user = get_user_by_student_id(db, student_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


def get_admin_user(
    current_user: User = Depends(get_current_user),
):
    """管理员鉴权 — 仅允许 admin 账号访问管理接口"""
    if current_user.student_id != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
