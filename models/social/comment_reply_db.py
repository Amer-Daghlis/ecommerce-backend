from models.social.comment_reply_model import CommentReply

def insert_reply(db, data):
    reply = CommentReply(
        user_id=data.user_id,
        comment_id=data.comment_id,
        reply_content=data.reply_content
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply
