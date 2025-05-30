from pydantic import BaseModel
from datetime import datetime

class ReplyCreate(BaseModel):
    user_id: int
    comment_id: int
    reply_content: str

class ReplyOut(BaseModel):
    reply_id: int
    user_id: int
    comment_id: int
    reply_content: str
    reply_date: datetime

    class Config:
        from_attributes = True
