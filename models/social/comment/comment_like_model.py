from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class CommentLike(Base):
    __tablename__ = "comment_likes"

    comment_id = Column(Integer, ForeignKey("comment.comment_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    liked_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")