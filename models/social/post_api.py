from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social import post_schema, post_db
from models.social.post_model import Post, AttachmentPost
from models.social.post_schema import PostCreate, PostOut

router = APIRouter(prefix="/posts", tags=["Posts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/new", response_model=PostOut)
def create_new_post(data: PostCreate, db: Session = Depends(get_db)):
    try:
        new_post = post_db.create_post(db, data)

        # استرجاع الصور من جدول attachmentpost
        attachments = db.query(AttachmentPost).filter(
            AttachmentPost.post_id == new_post.post_id
        ).all()

        attachment_links = [a.attachment_link for a in attachments]

        return {
            "post_id": new_post.post_id,
            "user_id": new_post.user_id,
            "post_title": new_post.post_title,
            "post_content": new_post.post_content,
            "category": new_post.category,
            "post_date": str(new_post.post_date),
            "attachments": attachment_links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create post: {e}")
