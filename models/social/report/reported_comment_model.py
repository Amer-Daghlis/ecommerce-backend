from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime  # ✅ هنا التصحيح
from pydantic import BaseModel

class ReportedComment(Base):
    __tablename__ = "reported_comment"

    reported_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    comment_id = Column(Integer, ForeignKey("comment.comment_id"))
    note = Column(String(255))
    report_date = Column(DateTime, default=datetime.utcnow)  # ✅ تم تصحيحها
    status = Column(Enum("pending", "rejected", name="report_comment_status"), default="pending")

    comment = relationship("Comment", back_populates="reports")
    user = relationship("User") 

class ReportCommentIn(BaseModel):
    user_id: int
    comment_id: int
    note: str


class ReportCommentOut(BaseModel):
    message: str
    report_date: datetime
    comment_status: str  # ✅ الحالة الجديدة

    model_config = {
        "from_attributes": True
    }
