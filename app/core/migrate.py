"""
数据库迁移模块 — 自动补全缺失的列

每次新增模型字段时，在此添加对应的 ALTER TABLE 语句。
无需手动删库即可完成 schema 变更。
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine


def migrate_db(engine: Engine) -> None:
    """检查并补全数据库中缺失的列"""
    with engine.connect() as conn:
        # ─── users 表 ───
        result = conn.execute(text("PRAGMA table_info(users)"))
        user_cols = {row[1] for row in result}

        if "addresses" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN addresses JSON DEFAULT '[]'"))
        if "active_address_index" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN active_address_index INTEGER DEFAULT 0"))
        if "security_question" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN security_question VARCHAR DEFAULT '你的第一只宠物叫什么名字？'"))
        if "security_answer" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN security_answer VARCHAR DEFAULT '小白'"))

        # ─── orders 表 ───
        result = conn.execute(text("PRAGMA table_info(orders)"))
        order_cols = {row[1] for row in result}

        if "student_id" not in order_cols:
            conn.execute(text("ALTER TABLE orders ADD COLUMN student_id VARCHAR DEFAULT ''"))

        # ─── shops 表 ───
        result = conn.execute(text("PRAGMA table_info(shops)"))
        shop_cols = {row[1] for row in result}

        if "image" not in shop_cols:
            conn.execute(text("ALTER TABLE shops ADD COLUMN image VARCHAR DEFAULT '🍽️'"))

        conn.commit()
