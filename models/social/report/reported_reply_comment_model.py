from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime
from pydantic import BaseModel

class ReportedCommentReply(Base):
    __tablename__ = "reported_comment_reply"

    reported_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    reply_id = Column(Integer, ForeignKey("comment_reply.reply_id"))
    note = Column(String(255))
    report_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("pending", "rejected", name="report_reply_status"), default="pending")

    reply = relationship("CommentReply", back_populates="reports")  # ✅ بدون import مباشر


class ReportReplyIn(BaseModel):
    user_id: int
    reply_id: int
    note: str

class ReportReplyOut(BaseModel):
    message: str
    report_date: datetime
    reply_status: str

    model_config = {
        "from_attributes": True
    }
