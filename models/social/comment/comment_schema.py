from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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


class UserLikeInfo(BaseModel):
    user_id: int
    name: str
    photo: Optional[str]

    class Config:
        from_attributes = True

class CommentWithLikesOut(BaseModel):
    comment_id: int
    liked_users: List[UserLikeInfo]

    class Config:
        from_attributes = True
