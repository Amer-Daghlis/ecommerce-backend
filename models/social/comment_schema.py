from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    user_id: int
    post_id: int
    comment_content: str

class CommentOut(BaseModel):
    comment_id: int
    user_id: int
    post_id: int
    comment_content: str
    comment_date: datetime

    class Config:
        from_attributes = True
