from sqlalchemy.orm import Session
from models.social.comment_model import Comment
from sqlalchemy import extract

def count_comments_by_month(db: Session, year: int, month: int):
    return db.query(Comment).filter(
        extract('year', Comment.comment_date) == year,
        extract('month', Comment.comment_date) == month
    ).count()


def insert_comment(db: Session, data):
    new_comment = Comment(
        user_id=data.user_id,
        post_id=data.post_id,
        comment_content=data.comment_content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment