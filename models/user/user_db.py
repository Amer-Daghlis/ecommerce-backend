from sqlalchemy import Column, Integer, String, Boolean, Date, Enum
from sqlalchemy.orm import Session
from models.database import Base  # Not user_db itself
from .user_schema import UserCreate
from .security import hash_password
import enum
from datetime import datetime

#  Define address enum
class AddressEnum(enum.Enum):
    Jenin = "Jenin"
    Tulkarm = "Tulkarm"
    Nablus = "Nablus"
    Qalqilya = "Qalqilya"
    Tubas = "Tubas"
    Salfit = "Salfit"
    Ramallah = "Ramallah and Al-Bireh"
    Jericho = "Jericho and Al-Aghwar"
    Bethlehem = "Bethlehem"
    Hebron = "Hebron"
    Jerusalem = "Jerusalem"

#  User ORM model
class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False)
    user_password = Column(String(255), nullable=False)
    user_name = Column(String(255))
    phone_number = Column(String(20))
    user_status = Column(Boolean)
    signed_at = Column(Date)
    community_activity_count = Column(Integer, default=0)
    address = Column(Enum(AddressEnum), nullable=True)  # ✅ New field

# Create a new user (sign up)
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


def get_or_create_google_user(db: Session, email: str, name: str):
    user = db.query(User).filter_by(user_email=email).first()
    if user:
        return user

    user = User(
        user_email=email,
        user_name=name,
        user_status=True,
        signed_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Get signup date of a user
def get_user_signup_date(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        return user.signed_at
    return None


# ✅ Get user address by ID
def get_user_address(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    return user.address if user else None



#  Get only contact info for user
def get_user_contact_info(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    return user  # We return the whole user object, Pydantic will filter fields
