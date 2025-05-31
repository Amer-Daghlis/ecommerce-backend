from pydantic import BaseModel
from datetime import date
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

class UserVerify(BaseModel):
    user_email: str

class CodeVerification(BaseModel):
    email: str
    code: str

class CheckUserEmailDefine(BaseModel):
    user_email: str
#************************************** Admin Section *****************************************#
class AdminUserOut(BaseModel):
    id: int
    name: str | None = None
    email: str
    phone: str | None = None
    location: str | None = None  
    orders: int
    spent: float
    lastOrder: date | None = None
    status: int  
    avatar: str | None = None
    signed_at: date | None = None

    class Config:
        from_attributes = True

class MonthlyUserJoin(BaseModel):
    month: int
    year: int
    total_users: float

    class Config:
        from_attributes = True


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    name = Column(String(255))       # ✅ تأكد إنه موجود
    photo = Column(String(255))      # ✅ تأكد إنه موجود
