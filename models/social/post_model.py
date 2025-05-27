from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    post_title = Column(String(255))
    post_content = Column(Text)
    post_date = Column(DateTime, default=datetime.datetime.utcnow)

    comments = relationship("Comment", back_populates="post")
    reports = relationship("ReportedPost", back_populates="post")
