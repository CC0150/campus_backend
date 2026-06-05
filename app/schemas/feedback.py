from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """学生提交反馈/留言"""
    type: str  # 'contact' | 'feedback'
    content: str
    category: str = ""  # 仅 type='feedback' 时使用


class FeedbackReply(BaseModel):
    """管理员回复"""
    reply: str


class FeedbackItem(BaseModel):
    """反馈列表项（返回给前端）"""
    id: int
    student_id: str = Field(alias="studentId")
    type: str
    category: str = ""
    content: str
    reply: str | None = None
    status: str = "pending"
    student_read: bool = Field(default=True, alias="studentRead")
    created_at: str = Field(alias="createdAt")

    model_config = {"from_attributes": True, "populate_by_name": True}


class UnreadCount(BaseModel):
    """未读回复数"""
    contact: int = 0
    feedback: int = 0
    total: int = 0
