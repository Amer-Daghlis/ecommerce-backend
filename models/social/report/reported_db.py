from sqlalchemy.orm import Session
from models.social.report.reported_post_model import ReportedPost
from models.social.report.reported_comment_model import ReportedComment
from sqlalchemy import extract, Column
from datetime import datetime 
from models.social.comment.comment_model import Comment



# ✅ استيراد النماذج المطلوبة
from models.social.post.post_model import Post
from fastapi import HTTPException

def count_reported_content_by_month(db: Session, year: int, month: int):
    post_reports = db.query(ReportedPost).filter(
        extract('year', ReportedPost.report_date) == year,
        extract('month', ReportedPost.report_date) == month
    ).count()

    comment_reports = db.query(ReportedComment).filter(
        extract('year', ReportedComment.report_date) == year,
        extract('month', ReportedComment.report_date) == month
    ).count()

    return post_reports + comment_reports

def report_post(db: Session, user_id: int, post_id: int, note: str):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # لا تسمح بالتبليغ على منشور محذوف
    if post.status == "removed":
        raise HTTPException(status_code=400, detail="You cannot report a removed post")

    # تحقق إذا سبق وتم التبليغ من نفس المستخدم على نفس المنشور
    existing_report = db.query(ReportedPost).filter(
        ReportedPost.user_id == user_id,
        ReportedPost.post_id == post_id
    ).first()
    if existing_report:
        raise HTTPException(status_code=400, detail="You already reported this post")

    # غيّر الحالة إلى "reported" إذا كانت "normal"
    if post.status == "normal":
        post.status = "reported"

    # أنشئ التبليغ
    report = ReportedPost(
        user_id=user_id,
        post_id=post_id,
        note=note,
        report_date=datetime.utcnow(),
        status="pending"
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report.report_date, post.status


def report_comment(db: Session, user_id: int, comment_id: int, note: str):
    comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.status == "removed":
        raise HTTPException(status_code=400, detail="You cannot report a removed comment")

    existing_report = db.query(ReportedComment).filter(
        ReportedComment.user_id == user_id,
        ReportedComment.comment_id == comment_id
    ).first()
    if existing_report:
        raise HTTPException(status_code=400, detail="You already reported this comment")

    # ✅ تعديل حالة التعليق
    if comment.status == "normal":
        comment.status = "reported"

    report = ReportedComment(
        user_id=user_id,
        comment_id=comment_id,
        note=note,
        report_date=datetime.utcnow(),
        status="pending"
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report.report_date, comment.status
