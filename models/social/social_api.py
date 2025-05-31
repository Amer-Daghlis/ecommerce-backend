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
from sqlalchemy.orm import joinedload, subqueryload
from collections import defaultdict
from models.social.post.post_model import AttachmentPost

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
def get_all_posts_full_json(db: Session = Depends(get_db)):
    try:
        posts = db.query(Post).filter(Post.status != "removed").all()
        all_users = {u.user_id: u for u in db.query(User).all()}
        all_comments = db.query(Comment).filter(Comment.status != "removed").all()
        all_replies = db.query(CommentReply).all()
        all_post_likes = db.query(PostLike).all()
        all_comment_likes = db.query(CommentLike).all()
        all_reply_likes = db.query(CommentReplyLike).all()
        all_attachments = db.query(AttachmentPost).all()

        post_likes_map = defaultdict(int)
        comment_likes_map = defaultdict(int)
        reply_likes_map = defaultdict(int)
        attachments_map = defaultdict(list)

        for l in all_post_likes:
            post_likes_map[l.post_id] += 1
        for l in all_comment_likes:
            comment_likes_map[l.comment_id] += 1
        for l in all_reply_likes:
            reply_likes_map[l.reply_id] += 1
        for a in all_attachments:
            attachments_map[a.post_id].append(a.attachment_link)

        comment_replies_map = defaultdict(list)
        for r in all_replies:
            comment_replies_map[r.comment_id].append(r)

        post_comments_map = defaultdict(list)
        for c in all_comments:
            post_comments_map[c.post_id].append(c)

        result = []
        for p in posts:
            user = all_users.get(p.user_id)
            post_comments = post_comments_map.get(p.post_id, [])

            post_obj = {
                "post_id": p.post_id,
                "title": p.post_title or "",
                "content": p.post_content or "",
                "user": {
                    "name": user.user_name if user else "Unknown",
                    "username": (user.user_email.split("@")[0] if user else ""),
                    "photo": user.photo or "/placeholder.svg?height=40&width=40&text=A"
                },
                "date": str(p.post_date),
                "likes": post_likes_map.get(p.post_id, 0),
                "comments": len(post_comments),
                "imageAttachments": attachments_map.get(p.post_id, []),
                "category": p.category or "Uncategorized",
                "postComments": []
            }

            for c in post_comments:
                comment_user = all_users.get(c.user_id)
                comment_obj = {
                    "id": c.comment_id,
                    "author": {
                        "name": comment_user.user_name if comment_user else "Unknown",
                        "username": (comment_user.user_email.split("@")[0] if comment_user else ""),
                        "avatar": comment_user.photo or "/placeholder.svg?height=40&width=40&text=A"
                    },
                    "content": c.comment_content,
                    "date": str(c.comment_date),
                    "likes": comment_likes_map.get(c.comment_id, 0),
                    "replies": []
                }

                for r in comment_replies_map.get(c.comment_id, []):
                    reply_user = all_users.get(r.user_id)
                    reply_obj = {
                        "id": r.reply_id,
                        "author": {
                            "name": reply_user.user_name if reply_user else "Unknown",
                            "username": (reply_user.user_email.split("@")[0] if reply_user else ""),
                            "avatar": reply_user.photo or "/placeholder.svg?height=40&width=40&text=A"
                        },
                        "content": r.reply_content,
                        "date": str(r.reply_date)
                    }
                    if reply_likes_map.get(r.reply_id):
                        reply_obj["likes"] = reply_likes_map[r.reply_id]

                    comment_obj["replies"].append(reply_obj)

                post_obj["postComments"].append(comment_obj)

            result.append(post_obj)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching full post data: {str(e)}")