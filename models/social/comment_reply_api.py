from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social import comment_reply_schema, comment_reply_db

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
