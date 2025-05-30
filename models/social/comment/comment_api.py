from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social.comment import comment_schema, comment_db
from models.social.comment import comment_like_schema, comment_like_model
from models.social.comment import comment_like_db

router = APIRouter(prefix="/comments", tags=["Comments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/new", response_model=comment_schema.CommentOut)
def create_comment(data: comment_schema.CommentCreate, db: Session = Depends(get_db)):
    try:
        return comment_db.insert_comment(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert comment: {e}")

@router.post("/like", tags=["Likes"])
def like_comment(data: comment_like_schema.LikeComment, db: Session = Depends(get_db)):
    try:
        return comment_like_db.like_comment(db, data.comment_id, data.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to like comment: {e}")