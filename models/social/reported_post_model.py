from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class ReportedPost(Base):
    __tablename__ = "reported_post"

    report_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    reason = Column(String(255))
    report_date = Column(DateTime, default=datetime.datetime.utcnow)

    post = relationship("Post", back_populates="reports")
