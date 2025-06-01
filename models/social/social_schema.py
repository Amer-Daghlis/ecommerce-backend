from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import Union

class SocialAnalytics(BaseModel):
    current_month_posts: int
    previous_month_posts: int
    current_month_comments: int
    previous_month_comments: int
    current_month_users: int
    previous_month_users: int
    current_month_reports: int
    previous_month_reports: int

class UserSocialInfo(BaseModel):
    id: int
    name: str
    username: str
    email: str
    avatar: Optional[str]
    status: Optional[Union[str, bool]]
    joined: str
    posts: int
    comments: int
    likes: int
    reports: int
    engagement: int
    location: Optional[str]

    class Config:
        from_attributes = True
