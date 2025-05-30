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
