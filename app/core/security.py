"""
安全模块 — JWT 令牌生成 / 密码哈希 / 令牌解码

提供以下核心功能：
1. 基于 HS256 的 JWT 令牌生成与解码
2. 基于 bcrypt 的密码哈希与校验
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

# ═══════════════════════════════════════════════════════════
# 常量配置
# ═══════════════════════════════════════════════════════════

# JWT 密钥（生产环境请替换为环境变量中的强随机字符串）
SECRET_KEY = "campus-ordering-secret-key-change-in-production"

# JWT 签名算法
ALGORITHM = "HS256"

# 令牌过期时长（分钟），默认 24 小时
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ═══════════════════════════════════════════════════════════
# 密码上下文 — bcrypt 加密方案
# ═══════════════════════════════════════════════════════════
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """对明文密码进行 bcrypt 哈希加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否与已存储的 bcrypt 哈希值匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    生成 JWT 访问令牌

    参数:
        data: 要编码到令牌中的自定义数据字典（如 {"sub": student_id}）

    返回:
        编码后的 JWT 字符串
    """
    to_encode = data.copy()
    # 设置令牌过期时间（UTC）
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    解码并验证 JWT 令牌

    参数:
        token: 客户端传入的 Bearer 令牌字符串

    返回:
        解码后的 payload 字典；验证失败则返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
