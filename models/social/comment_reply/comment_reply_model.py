from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class CommentReply(Base):
    __tablename__ = "comment_reply"

    reply_id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comment.comment_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    reply_content = Column(Text)
    reply_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default="normal")

