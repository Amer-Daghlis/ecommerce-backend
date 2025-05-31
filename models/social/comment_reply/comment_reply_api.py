from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social.comment_reply import comment_reply_schema, comment_reply_db
from models.social.comment_reply import comment_reply_like_db, comment_reply_like_schema
from models.social.comment_reply.comment_reply_schema import CommentReplyWithLikesOut
from typing import List
router = APIRouter(prefix="/replies", tags=["Replies"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/new", response_model=comment_reply_schema.ReplyOut)
def create_reply(data: comment_reply_schema.ReplyCreate, db: Session = Depends(get_db)):
    try:
        return comment_reply_db.insert_reply(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert reply: {e}")


@router.post("/like", tags=["Likes"])
def like_reply(data: comment_reply_like_schema.LikeReply, db: Session = Depends(get_db)):
    try:
        existing_like = db.query(comment_reply_like_db.CommentReplyLike).filter_by(reply_id=data.reply_id, user_id=data.user_id).first()

        if existing_like:
            db.delete(existing_like)
            db.commit()
            return {"message": "Unlike successfully"}
        else:
            new_like = comment_reply_like_db.CommentReplyLike(reply_id=data.reply_id, user_id=data.user_id)
            db.add(new_like)
            db.commit()
            return {"message": "Liked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {e}")


@router.get("/all-with-likes", response_model=List[CommentReplyWithLikesOut])
def get_all_comment_replies_with_likes(db: Session = Depends(get_db)):
    try:
        return comment_reply_db.get_all_comment_replies_with_likes(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch comment replies with likes: {e}")
