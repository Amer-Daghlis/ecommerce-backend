from pydantic import BaseModel

class LikeComment(BaseModel):
    comment_id: int
    user_id: int
