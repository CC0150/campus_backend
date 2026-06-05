"""反馈接口 — 学生提交留言/反馈 + 管理员查看/回复"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
from app.schemas.common import success_response
from app.schemas.feedback import FeedbackCreate, FeedbackReply, FeedbackItem, UnreadCount
from app.services import feedback_service

router = APIRouter(tags=["feedback"])


# ─── 学生端 ─────────────────────────────────────────────

@router.post("/feedback")
def submit_feedback(
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """学生提交留言或反馈"""
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="内容不能为空")
    if body.type not in ("contact", "feedback"):
        raise HTTPException(status_code=400, detail="类型无效")

    fb = feedback_service.create_feedback(
        db,
        student_id=current_user.student_id,
        type_=body.type,
        content=body.content.strip(),
        category=body.category,
    )
    return success_response(
        data=FeedbackItem.model_validate(fb).model_dump(by_alias=True),
        msg="提交成功",
    )


@router.get("/feedback/my")
def get_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """学生查看自己的留言/反馈历史"""
    items = feedback_service.get_my_feedback(db, current_user.student_id)
    return success_response(
        data=[FeedbackItem.model_validate(i).model_dump(by_alias=True) for i in items],
    )


@router.get("/feedback/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取学生未读回复数"""
    counts = feedback_service.get_unread_count(db, current_user.student_id)
    return success_response(data=counts)


@router.patch("/feedback/{feedback_id}/read")
def mark_feedback_read(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记单条反馈为已读"""
    ok = feedback_service.mark_as_read(db, feedback_id, current_user.student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="反馈不存在或无权操作")
    return success_response(msg="已标记为已读")


@router.patch("/feedback/read-all")
def mark_all_feedback_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量标记所有未读反馈为已读"""
    count = feedback_service.mark_all_as_read(db, current_user.student_id)
    return success_response(data={"count": count}, msg=f"已标记 {count} 条为已读")


@router.delete("/feedback/{feedback_id}")
def delete_my_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """学生删除自己的某条反馈"""
    ok = feedback_service.delete_feedback(db, feedback_id, current_user.student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="反馈不存在或无权删除")
    return success_response(msg="已删除")


@router.delete("/feedback/clear-all")
def clear_all_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """学生清空自己的所有反馈"""
    count = feedback_service.delete_all_my_feedback(db, current_user.student_id)
    return success_response(data={"count": count}, msg=f"已清空 {count} 条消息")


# ─── 管理端 ─────────────────────────────────────────────

admin_router = APIRouter(prefix="/admin", tags=["admin-feedback"])


@admin_router.get("/feedback")
def get_all_feedback(
    keyword: str | None = Query(default=None, description="搜索关键词（内容/学号/回复）"),
    type: str | None = Query(default=None, description="类型筛选 contact|feedback"),
    status: str | None = Query(default=None, description="状态筛选 pending|replied"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """管理员查看所有反馈，支持关键词/类型/状态筛选"""
    items = feedback_service.get_all_feedback(db, keyword=keyword, type_=type, status=status)
    return success_response(
        data=[FeedbackItem.model_validate(i).model_dump(by_alias=True) for i in items],
    )


@admin_router.put("/feedback/{feedback_id}/reply")
def reply_feedback(
    feedback_id: int,
    body: FeedbackReply,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """管理员回复反馈"""
    if not body.reply.strip():
        raise HTTPException(status_code=400, detail="回复内容不能为空")

    fb = feedback_service.reply_feedback(db, feedback_id, body.reply.strip())
    if fb is None:
        raise HTTPException(status_code=404, detail="反馈不存在")

    return success_response(
        data=FeedbackItem.model_validate(fb).model_dump(by_alias=True),
        msg="回复成功",
    )


@admin_router.delete("/feedback/{feedback_id}")
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """管理员删除某条反馈"""
    ok = feedback_service.delete_feedback(db, feedback_id)
    if not ok:
        raise HTTPException(status_code=404, detail="反馈不存在")
    return success_response(msg="已删除")
