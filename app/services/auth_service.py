"""
认证服务 — 登录校验 / 用户注册 / 用户查询

业务逻辑层，负责：
1. 用户注册：校验学号是否已存在，创建新用户
2. 登录校验：明文密码与 bcrypt 哈希比对，签发 JWT
3. 用户查询：按学号检索
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password, create_access_token, get_password_hash


def register_user(db: Session, student_id: str, name: str, password: str) -> User:
    """
    注册新用户

    参数:
        db: 数据库会话
        student_id: 学号（唯一标识）
        name: 昵称/姓名
        password: 明文密码（将 bcrypt 加密后存储）

    返回:
        新创建的 User 实例

    异常:
        ValueError — 学号已被注册
    """
    # 检查学号是否已存在
    existing = db.query(User).filter(User.student_id == student_id).first()
    if existing is not None:
        raise ValueError("该学号已被注册")

    # 创建用户对象
    user = User(
        student_id=student_id,
        name=name,
        password_hash=get_password_hash(password),
        balance=50.0,  # 新用户默认余额 50 元
        avatar="🧑‍🎓",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, student_id: str, password: str) -> str | None:
    """
    验证用户身份并签发 JWT 令牌

    流程：
    1. 通过学号查询 users 表
    2. 若用户不存在 → 返回 None
    3. 验证明文密码与数据库中的 bcrypt 哈希
    4. 验证通过 → 签发包含 sub 字段的 JWT 令牌
    5. 密码不匹配 → 返回 None

    参数:
        db: 数据库会话（由 FastAPI Depends 注入）
        student_id: 学号
        password: 明文密码

    返回:
        成功时返回 JWT 令牌字符串；失败时返回 None
    """
    # 第一步：按学号查询用户
    user = db.query(User).filter(User.student_id == student_id).first()
    if user is None:
        return None

    # 第二步：校验密码（bcrypt）
    if not verify_password(password, user.password_hash):
        return None

    # 第三步：签发 JWT，将学号存入 sub 字段
    return create_access_token({"sub": user.student_id})


def get_user_by_student_id(db: Session, student_id: str) -> User | None:
    """
    根据学号从数据库中查询用户记录

    参数:
        db: 数据库会话
        student_id: 学号

    返回:
        User 模型实例；不存在则返回 None
    """
    return db.query(User).filter(User.student_id == student_id).first()
