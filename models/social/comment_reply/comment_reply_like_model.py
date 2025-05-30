from sqlalchemy import Column, Integer, DateTime, ForeignKey
from models.database import Base
import datetime
from sqlalchemy.orm import relationship

class CommentReplyLike(Base):
    __tablename__ = "comment_reply_likes"

    reply_id = Column(Integer, ForeignKey("comment_reply.reply_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    liked_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")