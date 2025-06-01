from sqlalchemy.orm import Session
from models.social.report.reported_post_model import ReportedPost
from models.social.report.reported_comment_model import ReportedComment
from sqlalchemy import extract, Column
from datetime import datetime 
from models.social.comment.comment_model import Comment
from models.social.comment_reply.comment_reply_model import CommentReply
from models.social.report.reported_reply_comment_model import ReportedCommentReply  



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


def report_reply(db: Session, user_id: int, reply_id: int, note: str):
    reply = db.query(CommentReply).filter(CommentReply.reply_id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    if reply.status == "removed":
        raise HTTPException(status_code=400, detail="You cannot report a removed reply")

    existing = db.query(ReportedCommentReply).filter(
        ReportedCommentReply.user_id == user_id,
        ReportedCommentReply.reply_id == reply_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already reported this reply")

    if reply.status == "normal":
        reply.status = "reported"

    report = ReportedCommentReply(
        user_id=user_id,
        reply_id=reply_id,
        note=note,
        report_date=datetime.utcnow(),
        status="pending"
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report.report_date, reply.status
import random
from sqlalchemy.orm import Session, joinedload
from models.user.user_db import User

def get_random_reported_items(db: Session):
    result = []

    # 🔹 Random Reported Post
    post_reports = db.query(ReportedPost)\
        .options(joinedload(ReportedPost.post).joinedload(Post.user), joinedload(ReportedPost.user))\
        .all()
    if post_reports:
        random_post = random.choice(post_reports)
        result.append({
            "user_name": random_post.post.user.user_name if random_post.post and random_post.post.user else "Unknown",
            "reported_by": random_post.user.user_name if random_post.user else "Unknown",
            "title_or_content": random_post.post.post_title if random_post.post else "No content",
            "type": "post"
        })

    # 🔹 Random Reported Comment
    comment_reports = db.query(ReportedComment)\
        .options(joinedload(ReportedComment.comment).joinedload(Comment.user), joinedload(ReportedComment.user))\
        .all()
    if comment_reports:
        random_comment = random.choice(comment_reports)
        result.append({
            "user_name": random_comment.comment.user.user_name if random_comment.comment and random_comment.comment.user else "Unknown",
            "reported_by": random_comment.user.user_name if random_comment.user else "Unknown",
            "title_or_content": random_comment.comment.comment_content if random_comment.comment else "No content",
            "type": "comment"
        })

    # 🔹 Random Reported Reply
    reply_reports = db.query(ReportedCommentReply)\
        .options(joinedload(ReportedCommentReply.reply).joinedload(CommentReply.user), joinedload(ReportedCommentReply.user))\
        .all()
    if reply_reports:
        random_reply = random.choice(reply_reports)
        result.append({
            "user_name": random_reply.reply.user.user_name if random_reply.reply and random_reply.reply.user else "Unknown",
            "reported_by": random_reply.user.user_name if random_reply.user else "Unknown",
            "title_or_content": random_reply.reply.reply_content if random_reply.reply else "No content",
            "type": "reply"
        })

    return result


def get_all_reported_data(db: Session):
    results = []

    # 🔸 Posts
    post_reports = db.query(ReportedPost)\
        .options(joinedload(ReportedPost.post).joinedload(Post.user), joinedload(ReportedPost.user))\
        .all()
    for report in post_reports:
        results.append({
            "id": report.reported_id,
            "type": "Post",
            "content": report.post.post_content if report.post else "No content",
            "user": report.post.user.user_name if report.post and report.post.user else "Unknown",
            "reportedBy": report.user.user_name if report.user else "Unknown",
            "reportedDate": report.report_date.strftime("%Y-%m-%d"),
            "status": report.status,
            "postTitle": report.post.post_title if report.post else "No title",
            "notes": report.note
        })

    # 🔸 Comments
    comment_reports = db.query(ReportedComment)\
        .options(joinedload(ReportedComment.comment).joinedload(Comment.user), joinedload(ReportedComment.user))\
        .all()
    for report in comment_reports:
        results.append({
            "id": report.reported_id,
            "type": "Comment",
            "content": report.comment.comment_content if report.comment else "No content",
            "user": report.comment.user.user_name if report.comment and report.comment.user else "Unknown",
            "reportedBy": report.user.user_name if report.user else "Unknown",
            "reportedDate": report.report_date.strftime("%Y-%m-%d"),
            "status": report.status,
            "postTitle": report.comment.post_title if hasattr(report.comment, "post_title") else None,
            "notes": report.note
        })

    # 🔸 Replies
    reply_reports = db.query(ReportedCommentReply)\
        .options(joinedload(ReportedCommentReply.reply).joinedload(CommentReply.user), joinedload(ReportedCommentReply.user))\
        .all()
    for report in reply_reports:
        results.append({
            "id": report.reported_id,
            "type": "Reply",
            "content": report.reply.reply_content if report.reply else "No content",
            "user": report.reply.user.user_name if report.reply and report.reply.user else "Unknown",
            "reportedBy": report.user.user_name if report.user else "Unknown",
            "reportedDate": report.report_date.strftime("%Y-%m-%d"),
            "status": report.status,
            "postTitle": None,  # إذا بدك تجيب عنوان المنشور الأساسي تبع الرد، بنربطها لاحقًا
            "notes": report.note
        })

    return results


def set_report_status(db: Session, report_id: int, report_type: str, new_status: str):
    report_type = report_type.lower()

    if report_type == "post":
        report = db.query(ReportedPost).filter(ReportedPost.reported_id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report.status = new_status
        db.commit()

        # ✅ تحقق إذا لازم نرجع حالة المنشور إلى normal
        if new_status == "rejected":
            remaining = db.query(ReportedPost).filter(
                ReportedPost.post_id == report.post_id,
                ReportedPost.status != "rejected"
            ).count()
            if remaining == 0:
                post = db.query(Post).filter(Post.post_id == report.post_id).first()
                if post:
                    post.status = "normal"
                    db.commit()

    elif report_type == "comment":
        report = db.query(ReportedComment).filter(ReportedComment.reported_id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report.status = new_status
        db.commit()

        if new_status == "rejected":
            remaining = db.query(ReportedComment).filter(
                ReportedComment.comment_id == report.comment_id,
                ReportedComment.status != "rejected"
            ).count()
            if remaining == 0:
                comment = db.query(Comment).filter(Comment.comment_id == report.comment_id).first()
                if comment:
                    comment.status = "normal"
                    db.commit()

    elif report_type == "reply":
        report = db.query(ReportedCommentReply).filter(ReportedCommentReply.reported_id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report.status = new_status
        db.commit()

        if new_status == "rejected":
            remaining = db.query(ReportedCommentReply).filter(
                ReportedCommentReply.reply_id == report.reply_id,
                ReportedCommentReply.status != "rejected"
            ).count()
            if remaining == 0:
                reply = db.query(CommentReply).filter(CommentReply.reply_id == report.reply_id).first()
                if reply:
                    reply.status = "normal"
                    db.commit()

    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    db.refresh(report)
    return {
        "message": f"{report_type.capitalize()} report status updated successfully",
        "report_id": report_id,
        "new_status": new_status
    }

