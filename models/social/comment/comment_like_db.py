from models.social.comment.comment_like_model import CommentLike
from sqlalchemy.orm import Session
from fastapi import HTTPException

def like_comment(db: Session, comment_id: int, user_id: int):
    existing = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already liked this comment")

    like = CommentLike(comment_id=comment_id, user_id=user_id)
    db.add(like)
    db.commit()
    return {"message": "Comment liked successfully"}
