from sqlalchemy import Column, String, Float, JSON, Integer

from app.models import Base


class User(Base):
    __tablename__ = "users"

    student_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    balance = Column(Float, default=50.0)
    avatar = Column(String, default="🧑‍🎓")
    # 收货地址列表（JSON 数组），初始为空
    addresses = Column(JSON, default=list)
    # 当前选中的地址索引
    active_address_index = Column(Integer, default=0)
    # 密保问题与答案
    security_question = Column(String, default="你的第一只宠物叫什么名字？")
    security_answer = Column(String, default="小白")
