from sqlalchemy.orm import Session
from models.social.comment.comment_model import Comment
from sqlalchemy import extract
from models.social.comment.comment_model import Comment
from models.social.comment.comment_like_model import CommentLike
from models.user.user_db import User

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


def get_all_comments_with_likes(db: Session):
    comments = db.query(Comment).all()
    result = []

    for comment in comments:
        likes = db.query(CommentLike).filter(CommentLike.comment_id == comment.comment_id).all()
        users = []

        for like in likes:
            user = db.query(User).filter(User.user_id == like.user_id).first()
            if user:
                users.append({
                    "user_id": user.user_id,
                    "name": user.user_name,
                    "photo": user.photo
                })

        result.append({
            "comment_id": comment.comment_id,
            "liked_users": users
        })

    return result
