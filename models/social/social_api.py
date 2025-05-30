from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social import social_db  
from models.social.post.post_model import Post
from models.social.comment.comment_model import Comment
from models.social.comment_reply.comment_reply_model import CommentReply
from models.social.post.post_like_model import PostLike
from models.social.comment.comment_like_model import CommentLike
from models.social.comment_reply.comment_reply_like_model import CommentReplyLike
from models.user.user_db import User
from sqlalchemy.orm import joinedload , subqueryload
from collections import defaultdict



router = APIRouter(prefix="/social", tags=["Social Media"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/analytics")
def get_social_analytics(db: Session = Depends(get_db)):
    try:
        return social_db.get_social_analytics(db)
    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@router.get("/posts/full")
def get_all_posts_full(db: Session = Depends(get_db)):
    try:
        posts = db.query(Post).filter(Post.status != "removed").all()
        comments = db.query(Comment).filter(Comment.status != "removed").all()
        replies = db.query(CommentReply).all()

        post_likes = db.query(PostLike).join(User, PostLike.user_id == User.user_id).all()
        comment_likes = db.query(CommentLike).join(User, CommentLike.user_id == User.user_id).all()
        reply_likes = db.query(CommentReplyLike).join(User, CommentReplyLike.user_id == User.user_id).all()

        from collections import defaultdict
        post_likes_map = defaultdict(list)
        for like in post_likes:
            post_likes_map[like.post_id].append({
                "user_id": like.user_id,
                "user_name": like.user.user_name,
                "user_image": like.user.photo,
                "like_date": like.liked_at,
            })

        comment_likes_map = defaultdict(list)
        for like in comment_likes:
            comment_likes_map[like.comment_id].append({
                "user_id": like.user_id,
                "user_name": like.user.user_name,
                "user_image": like.user.photo,
                "like_date": like.liked_at,
            })

        reply_likes_map = defaultdict(list)
        for like in reply_likes:
            reply_likes_map[like.reply_id].append({
                "user_id": like.user_id,
                "user_name": like.user.user_name,
                "user_image": like.user.photo,
                "like_date": like.liked_at,
            })

        # Group replies
        replies_map = defaultdict(list)
        for r in replies:
            replies_map[r.comment_id].append({
                "reply_id": r.reply_id,
                "user_id": r.user_id,
                "content": r.reply_content,
                "date": r.reply_date,
                "reply_likes": reply_likes_map.get(r.reply_id, [])
            })

        # Group comments
        comments_map = defaultdict(list)
        for c in comments:
            comments_map[c.post_id].append({
                "comment_id": c.comment_id,
                "user_id": c.user_id,
                "content": c.comment_content,
                "date": c.comment_date,
                "comment_likes": comment_likes_map.get(c.comment_id, []),
                "replies": replies_map.get(c.comment_id, [])
            })

        output = []
        for post in posts:
            output.append({
                "post_id": post.post_id,
                "title": post.post_title,
                "content": post.post_content,
                "date": post.post_date,
                "category": post.category,
                "user_id": post.user_id,
                "status": post.status,
                "post_likes": post_likes_map.get(post.post_id, []),
                "comments": comments_map.get(post.post_id, [])
            })

        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching full post data: {str(e)}")