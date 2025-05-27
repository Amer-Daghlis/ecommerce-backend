from sqlalchemy.orm import Session
from models.social.comment_model import Comment
from sqlalchemy import extract

def count_comments_by_month(db: Session, year: int, month: int):
    return db.query(Comment).filter(
        extract('year', Comment.comment_date) == year,
        extract('month', Comment.comment_date) == month
    ).count()
