from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class PostLike(Base):
    __tablename__ = "post_likes"

    post_id = Column(Integer, ForeignKey("posts.post_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    liked_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")  
    