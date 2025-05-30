from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.social.comment_reply.comment_reply_like_model import CommentReplyLike

def like_reply(db: Session, reply_id: int, user_id: int):
    existing = db.query(CommentReplyLike).filter_by(reply_id=reply_id, user_id=user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already liked this reply")

    like = CommentReplyLike(reply_id=reply_id, user_id=user_id)
    db.add(like)
    db.commit()
    return {"message": "Reply liked successfully"}
