from models.social.post.post_like_model import PostLike
from sqlalchemy.orm import Session
from fastapi import HTTPException

def like_post(db: Session, post_id: int, user_id: int):
    existing = db.query(PostLike).filter_by(post_id=post_id, user_id=user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already liked this post")
    
    like = PostLike(post_id=post_id, user_id=user_id)
    db.add(like)
    db.commit()
    return {"message": "Post liked successfully"}
