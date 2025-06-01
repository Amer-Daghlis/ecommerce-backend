from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime
report_date: datetime
from pydantic import BaseModel

class ReportedPost(Base):
    __tablename__ = "reported_post"

    reported_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    post_id = Column(Integer, ForeignKey("posts.post_id"))
    note = Column(String(255))
    report_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("pending", "rejected", name="report_status"), default="pending")

    post = relationship("Post", back_populates="reports")
    user = relationship("User") 

class ReportPostIn(BaseModel):
    user_id: int           # المستخدم الذي قدّم التبليغ
    post_id: int           # رقم المنشور
    note: str              # سبب التبليغ

# 📤 الإخراج (output): التأكيد بعد التبليغ
class ReportPostOut(BaseModel):
    message: str           # رسالة تأكيد
    report_date: datetime  # تاريخ التبليغ
    post_status: str       # الحالة الحالية للمنشور (normal / reported / removed)

    model_config = {
        "from_attributes": True  # مطلوب في Pydantic v2 بدلاً من orm_mode
    }
# 📥 الإدخال (input): البيانات المطلوبة لتبليغ منشور