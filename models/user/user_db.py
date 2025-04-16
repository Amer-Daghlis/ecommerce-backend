from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import Session
from models.database import Base
from .user_schema import UserCreate
from .security import hash_password

# SQLAlchemy ORM model for the User table
class User(Base):
    __tablename__ = "user"  # ✅ match actual MySQL table name (usually lowercase)

    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False)
    user_password = Column(String(255), nullable=False)
    user_name = Column(String(255))
    phone_number = Column(String(20))
    user_status = Column(Boolean)
    signed_at = Column(Date)
    community_activity_count = Column(Integer, default=0)

# --- Database Operation Methods ---

# ✅ Create a new user (sign up)
def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.user_password)
    new_user = User(
        user_email=user.user_email,
        user_password=hashed_pw,
        user_name=user.user_name,
        phone_number=user.phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ Get all users
def get_all_users(db: Session):
    return db.query(User).all()

# ✅ Get a user by their ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

# ✅ Get a user by their email (for login)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.user_email == email).first()

# ✅ Get users by name (for searching)
def get_users_by_name(db: Session, name: str):
    return db.query(User).filter(User.user_name.like(f"%{name}%")).all()

# ✅ Delete a user by ID
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user
