from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from datetime import datetime
from models.social.post.post_model import Post
from models.social.comment.comment_model import Comment
from models.social.report.reported_post_model import ReportedPost
from models.social.report.reported_comment_model import ReportedComment
from models.user.user_db import User  

def get_social_analytics(db: Session):
    now = datetime.utcnow()
    current_year, current_month = now.year, now.month

    # شهر سابق
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    def count_this_month(model, field):
        return db.query(func.count()).filter(
            extract('year', field) == current_year,
            extract('month', field) == current_month
        ).scalar()

    def count_last_month(model, field):
        return db.query(func.count()).filter(
            extract('year', field) == previous_year,
            extract('month', field) == previous_month
        ).scalar()

    result = {
        "current_month_posts": count_this_month(Post, Post.post_date),
        "previous_month_posts": count_last_month(Post, Post.post_date),

        "current_month_comments": count_this_month(Comment, Comment.comment_date),
        "previous_month_comments": count_last_month(Comment, Comment.comment_date),

        "current_month_reported": count_this_month(ReportedPost, ReportedPost.report_date) +
                                  count_this_month(ReportedComment, ReportedComment.report_date),
        "previous_month_reported": count_last_month(ReportedPost, ReportedPost.report_date) +
                                   count_last_month(ReportedComment, ReportedComment.report_date),

        "current_month_users": count_this_month(User, User.signed_at),
        "previous_month_users": count_last_month(User, User.signed_at),
    }

    return result

from models.social.comment_reply.comment_reply_model import CommentReply
from models.social.comment.comment_model import Comment
from models.social.post.post_model import Post
from models.social.post.post_like_model import PostLike
from models.social.comment.comment_like_model import CommentLike
from models.social.comment_reply.comment_reply_like_model import CommentReplyLike
from models.social.report.reported_post_model import ReportedPost
from models.social.report.reported_comment_model import ReportedComment
from sqlalchemy import distinct

def get_detailed_social_users(db: Session):
    # استخراج المستخدمين اللي إلهم نشاط
    post_user_ids = db.query(distinct(Post.user_id)).all()
    comment_user_ids = db.query(distinct(Comment.user_id)).all()
    reply_user_ids = db.query(distinct(CommentReply.user_id)).all()

    all_user_ids = set()
    for group in [post_user_ids, comment_user_ids, reply_user_ids]:
        all_user_ids.update([u[0] for u in group])

    # استرجاع المستخدمين النشطين
    users = db.query(User).filter(User.user_id.in_(all_user_ids)).all()

    result = []
    for user in users:
        post_count = db.query(func.count()).filter(Post.user_id == user.user_id).scalar()
        comment_count = db.query(func.count()).filter(Comment.user_id == user.user_id).scalar()
        reply_count = db.query(func.count()).filter(CommentReply.user_id == user.user_id).scalar()
        like_count = (
            db.query(func.count()).filter(PostLike.user_id == user.user_id).scalar() +
            db.query(func.count()).filter(CommentLike.user_id == user.user_id).scalar() +
            db.query(func.count()).filter(CommentReplyLike.user_id == user.user_id).scalar()
        )
        report_count = (
            db.query(func.count()).filter(ReportedPost.user_id == user.user_id).scalar() +
            db.query(func.count()).filter(ReportedComment.user_id == user.user_id).scalar()
        )

        engagement = post_count + comment_count + reply_count + like_count  # بإمكانك تغير المعادلة

        result.append({
            "id": user.user_id,
            "name": user.user_name,
            "username": user.user_name,
            "email": user.user_email,
            "avatar": user.photo,
            "status": user.user_status,
            "joined": str(user.signed_at),
            "posts": post_count,
            "comments": comment_count + reply_count,
            "likes": like_count,
            "reports": report_count,
            "engagement": engagement,
            "location": user.address
        })

    return result

def get_top_engaged_users(db: Session, limit: int = 5):
    post_counts = db.query(
        Post.user_id,
        func.count(Post.post_id).label("post_count")
    ).group_by(Post.user_id).subquery()

    comment_counts = db.query(
        Comment.user_id,
        func.count(Comment.comment_id).label("comment_count")
    ).group_by(Comment.user_id).subquery()

    results = db.query(
        User.user_name,
        User.phone_number.label("user_phone"),
        func.coalesce(post_counts.c.post_count, 0).label("post_count"),
        func.coalesce(comment_counts.c.comment_count, 0).label("comment_count"),
        (func.coalesce(post_counts.c.post_count, 0) + func.coalesce(comment_counts.c.comment_count, 0)).label("engagement_score")
    ).outerjoin(post_counts, User.user_id == post_counts.c.user_id)\
     .outerjoin(comment_counts, User.user_id == comment_counts.c.user_id)\
     .order_by((func.coalesce(post_counts.c.post_count, 0) + func.coalesce(comment_counts.c.comment_count, 0)).desc())\
     .limit(limit)\
     .all()

    return [
        {
            "user_name": row.user_name,
            "user_phone": row.user_phone or "",  # to avoid validation error
            "post_count": row.post_count,
            "comment_count": row.comment_count
        }
        for row in results
    ]
