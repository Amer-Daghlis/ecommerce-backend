from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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


class UserLikeInfo(BaseModel):
    user_id: int
    name: str
    photo: Optional[str]

    class Config:
        from_attributes = True

class CommentReplyWithLikesOut(BaseModel):
    reply_id: int
    liked_users: List[UserLikeInfo]

    class Config:
        from_attributes = True
