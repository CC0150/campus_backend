from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean

from app.models import Base


class Feedback(Base):
    """反馈/留言模型 — 学生提交建议或联系志愿者留言"""

    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("users.student_id"), nullable=False)
    type = Column(String, nullable=False)  # 'contact' | 'feedback'
    category = Column(String, default="")  # 仅 type='feedback' 时使用
    content = Column(Text, nullable=False)
    reply = Column(Text, nullable=True)  # 管理员回复
    status = Column(String, default="pending")  # 'pending' | 'replied'
    student_read = Column(Boolean, default=True)  # 学生端是否有未读回复
    student_deleted = Column(Boolean, default=False)  # 学生端软删除标记（仅对学生隐藏，管理端仍可见）
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
