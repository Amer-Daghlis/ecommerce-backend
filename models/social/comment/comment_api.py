from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social.comment import comment_schema, comment_db
from models.social.comment import comment_like_schema, comment_like_model
from models.social.comment import comment_like_db
from models.social.comment.comment_schema import CommentWithLikesOut
from typing import List
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
        existing_like = db.query(comment_like_model.CommentLike).filter_by(comment_id=data.comment_id, user_id=data.user_id).first()

        if existing_like:
            db.delete(existing_like)
            db.commit()
            return {"message": "Unlike successfully"}
        else:
            new_like = comment_like_model.CommentLike(comment_id=data.comment_id, user_id=data.user_id)
            db.add(new_like)
            db.commit()
            return {"message": "Liked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {e}")
    


@router.get("/all-with-likes", response_model=List[CommentWithLikesOut])
def get_all_comments_with_likes(db: Session = Depends(get_db)):
    try:
        return comment_db.get_all_comments_with_likes(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments with likes: {e}")
