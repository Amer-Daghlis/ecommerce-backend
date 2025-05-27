from pydantic import BaseModel

class SocialAnalytics(BaseModel):
    current_month_posts: int
    previous_month_posts: int
    current_month_comments: int
    previous_month_comments: int
    current_month_users: int
    previous_month_users: int
    current_month_reports: int
    previous_month_reports: int