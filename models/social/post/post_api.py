from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social.post import post_schema, post_db
from models.social.post.post_model import Post, AttachmentPost
from models.social.post.post_schema import PostCreate, PostOut
from models.social.post.post_like_model import PostLike
from models.social.post.post_like_schema import LikePost
from typing import List
from models.social.post.post_schema import PostWithLikesOut


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



# Post Like Endpoint

@router.post("/like", tags=["Likes"])
def like_post(data: LikePost, db: Session = Depends(get_db)):
    try:
        existing_like = db.query(PostLike).filter_by(post_id=data.post_id, user_id=data.user_id).first()

        if existing_like:
            db.delete(existing_like)
            db.commit()
            return {"message": "Unlike successfully"}
        else:
            new_like = PostLike(post_id=data.post_id, user_id=data.user_id)
            db.add(new_like)
            db.commit()
            return {"message": "Liked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {e}")


@router.get("/all-with-likes", response_model=List[PostWithLikesOut])
def get_all_posts_with_likes(db: Session = Depends(get_db)):
    try:
        return post_db.get_all_posts_with_likes(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts with likes: {e}")

@router.get("/top-performing", tags=["Analytics"])
def top_performing_posts(db: Session = Depends(get_db)):
    try:
        return post_db.get_top_performing_posts(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top posts: {e}")
