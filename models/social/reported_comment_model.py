from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

class ReportedComment(Base):
    __tablename__ = "reported_comment"

    report_id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comment.comment_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    reason = Column(String(255))
    report_date = Column(DateTime, default=datetime.datetime.utcnow)

    comment = relationship("Comment", back_populates="reports")
