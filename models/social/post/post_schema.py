from pydantic import BaseModel
from typing import List
from typing import Optional

class PostCreate(BaseModel):
    user_id: int
    post_title: str
    post_content: str
    category: Optional[str]
    attachments: List[str]

class PostOut(BaseModel):
    post_id: int
    user_id: int
    post_title: str
    post_content: str
    category: Optional[str]
    post_date: str
    attachments: List[str]

    class Config:
        from_attributes = True



class UserLikeInfo(BaseModel):
    user_id: int
    name: str
    photo: Optional[str]

    class Config:
        from_attributes = True


class PostWithLikesOut(BaseModel):
    post_id: int
    liked_users: List[UserLikeInfo]

    class Config:
        from_attributes = True
