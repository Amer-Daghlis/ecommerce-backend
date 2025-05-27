from sqlalchemy.orm import Session
from models.social.post_model import Post
from sqlalchemy import extract
from datetime import datetime

def count_posts_by_month(db: Session, year: int, month: int):
    return db.query(Post).filter(
        extract('year', Post.post_date) == year,
        extract('month', Post.post_date) == month
    ).count()
