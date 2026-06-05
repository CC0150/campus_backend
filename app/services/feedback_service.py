from sqlalchemy.orm import Session

from app.models.feedback import Feedback


def create_feedback(
    db: Session,
    student_id: str,
    type_: str,
    content: str,
    category: str = "",
) -> Feedback:
    """学生提交留言或反馈"""
    feedback = Feedback(
        student_id=student_id,
        type=type_,
        content=content,
        category=category,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_my_feedback(db: Session, student_id: str) -> list[Feedback]:
    """学生查看自己的留言/反馈历史（不包含已软删除的）"""
    return (
        db.query(Feedback)
        .filter(
            Feedback.student_id == student_id,
            Feedback.student_deleted == False,
        )
        .order_by(Feedback.created_at.desc())
        .all()
    )


def get_all_feedback(
    db: Session,
    keyword: str | None = None,
    type_: str | None = None,
    status: str | None = None,
) -> list[Feedback]:
    """管理员查看所有反馈，支持关键词/类型/状态筛选"""
    q = db.query(Feedback)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (Feedback.content.contains(keyword))
            | (Feedback.student_id.contains(keyword))
            | (Feedback.reply.contains(keyword))
        )
    if type_:
        q = q.filter(Feedback.type == type_)
    if status:
        q = q.filter(Feedback.status == status)
    return q.order_by(Feedback.created_at.desc()).all()


def reply_feedback(db: Session, feedback_id: int, reply: str) -> Feedback | None:
    """管理员回复反馈 — 自动标记学生未读"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        return None
    feedback.reply = reply
    feedback.status = "replied"
    feedback.student_read = False
    db.commit()
    db.refresh(feedback)
    return feedback


def mark_as_read(db: Session, feedback_id: int, student_id: str) -> bool:
    """学生标记某条反馈为已读"""
    feedback = (
        db.query(Feedback)
        .filter(Feedback.id == feedback_id, Feedback.student_id == student_id)
        .first()
    )
    if not feedback:
        return False
    feedback.student_read = True
    db.commit()
    return True


def mark_all_as_read(db: Session, student_id: str) -> int:
    """批量标记该学生所有未读反馈为已读（跳过已软删除的），返回标记数量"""
    count = (
        db.query(Feedback)
        .filter(
            Feedback.student_id == student_id,
            Feedback.student_read == False,
            Feedback.student_deleted == False,
        )
        .update({"student_read": True})
    )
    db.commit()
    return count


def get_unread_count(db: Session, student_id: str) -> dict:
    """获取学生未读回复数，按类型分组（不包含已软删除的）"""
    contact = (
        db.query(Feedback)
        .filter(
            Feedback.student_id == student_id,
            Feedback.type == "contact",
            Feedback.student_read == False,
            Feedback.student_deleted == False,
        )
        .count()
    )
    feedback = (
        db.query(Feedback)
        .filter(
            Feedback.student_id == student_id,
            Feedback.type == "feedback",
            Feedback.student_read == False,
            Feedback.student_deleted == False,
        )
        .count()
    )
    return {"contact": contact, "feedback": feedback, "total": contact + feedback}


def delete_feedback(db: Session, feedback_id: int, student_id: str | None = None) -> bool:
    """删除单条反馈。
    学生端（提供 student_id）：软删除，仅对学生隐藏，管理端仍可见。
    管理端（不提供 student_id）：硬删除，从数据库彻底移除。
    """
    q = db.query(Feedback).filter(Feedback.id == feedback_id)
    if student_id:
        q = q.filter(Feedback.student_id == student_id, Feedback.student_deleted == False)
    fb = q.first()
    if not fb:
        return False
    if student_id:
        # 学生端软删除
        fb.student_deleted = True
    else:
        # 管理端硬删除
        db.delete(fb)
    db.commit()
    return True


def delete_all_my_feedback(db: Session, student_id: str) -> int:
    """学生清空自己的所有反馈（软删除），返回标记数量"""
    count = (
        db.query(Feedback)
        .filter(
            Feedback.student_id == student_id,
            Feedback.student_deleted == False,
        )
        .update({"student_deleted": True})
    )
    db.commit()
    return count
