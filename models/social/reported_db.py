from sqlalchemy.orm import Session
from models.social.reported_post_model import ReportedPost
from models.social.reported_comment_model import ReportedComment
from sqlalchemy import extract

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
