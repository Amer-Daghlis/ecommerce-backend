from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    post_title = Column("title", String(255))  # ✅ حط اسم العمود الحقيقي
    post_content = Column("content", Text)     # ✅ نفس الشي
    post_date = Column(DateTime, default=datetime.datetime.utcnow)
    category = Column(String(100))
    status = Column(String(20), default="normal")

    comments = relationship("Comment", back_populates="post")
    reports = relationship("ReportedPost", back_populates="post")

class AttachmentPost(Base):
    __tablename__ = "attachmentpost"

    attachment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"))
    attachment_link = Column(String(255))
