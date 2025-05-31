from sqlalchemy.orm import Session
from models.social.post.post_model import Post
from sqlalchemy import extract
from datetime import datetime
from models.social.post.post_model import AttachmentPost
from models.user.user_db import User
from models.social.post.post_like_model import PostLike

def count_posts_by_month(db: Session, year: int, month: int):
    return db.query(Post).filter(
        extract('year', Post.post_date) == year,
        extract('month', Post.post_date) == month
    ).count()


def create_post(db: Session, data):
    new_post = Post(
        user_id=data.user_id,
        post_title=data.post_title,
        post_content=data.post_content,
        category=data.category
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    for link in data.attachments:
        attachment = AttachmentPost(
            post_id=new_post.post_id,
            attachment_link=link
        )
        db.add(attachment)

    db.commit()
    return new_post


def get_all_posts_with_likes(db: Session):
    posts = db.query(Post).all()
    result = []

    for post in posts:
        likes = db.query(PostLike).filter(PostLike.post_id == post.post_id).all()
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
            "post_id": post.post_id,
            "liked_users": users
        })

    return result

