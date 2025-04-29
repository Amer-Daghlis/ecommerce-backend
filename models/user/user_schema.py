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

# Schema for returning only signup date
class UserSignupDate(BaseModel):
    user_id: int
    signup_date: date

    class Config:
        orm_mode = True  
        

class UserAddress(BaseModel):
    user_id: int
    address: str

    class Config:
        orm_mode = True

 #  For user contact info
class UserContactInfo(BaseModel):
    user_id: int
    user_name: str | None
    user_email: str
    phone_number: str | None
    address: str | None  # will map from Enum to str

    class Config:
        from_attributes = True
