from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    user_email: str
    user_name: str | None = None
    phone_number: str | None = None

class UserCreate(UserBase):
    user_password: str

class UserOut(UserBase):
    user_id: int
    user_status: bool | None = None
    signed_at: date | None = None
    community_activity_count: int = 0

    class Config:
        orm_mode = True
