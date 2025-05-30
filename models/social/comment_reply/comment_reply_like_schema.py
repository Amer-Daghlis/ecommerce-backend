from pydantic import BaseModel

class LikeReply(BaseModel):
    reply_id: int
    user_id: int
