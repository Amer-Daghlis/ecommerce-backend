from models.social.comment_reply.comment_reply_model import CommentReply
from models.social.comment_reply.comment_reply_model import CommentReply
from models.social.comment_reply.comment_reply_like_model import CommentReplyLike
from models.user.user_db import User
from sqlalchemy.orm import Session

def insert_reply(db, data):
    reply = CommentReply(
        user_id=data.user_id,
        comment_id=data.comment_id,
        reply_content=data.reply_content
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


def get_all_comment_replies_with_likes(db: Session):
    replies = db.query(CommentReply).all()
    result = []

    for reply in replies:
        likes = db.query(CommentReplyLike).filter(CommentReplyLike.reply_id == reply.reply_id).all()
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
            "reply_id": reply.reply_id,
            "liked_users": users
        })

    return result
