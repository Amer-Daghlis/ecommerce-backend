from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from models.database import Base  # Not user_db itself
from .user_schema import UserCreate
from .security import hash_password
import enum
from datetime import datetime
from models.order.order_db import OrderTable
from sqlalchemy import func
from datetime import date
from sqlalchemy.orm import relationship
from sqlalchemy import extract, func

# Define address enum
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

# User ORM model
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
    address = Column(Enum(AddressEnum), nullable=True)
    photo = Column(String(255), nullable=True)
    signed_method = Column(String(255), nullable=False)
    token = Column(String(255), nullable=True)
    user_reported_times = Column(Integer, default=0)
    orders = relationship("OrderTable", back_populates="user")

# Create a new user (sign up) by email
def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.user_password)
    new_user = User(
        user_email=user.user_email,
        user_password=hashed_pw,
        user_name=user.user_name,
        signed_method = "Email verification",
        signed_at=date.today(),
        user_status = True,
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ Get all users
def get_all_users(db: Session):
    return db.query(User).all()

# ✅ Get a user by their ID

# ✅ Get a user by their email (for login)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.user_email == email).first()

# ✅ Get users by name (for searching)
def get_users_by_name(db: Session, name: str):
    return db.query(User).filter(User.user_name.like(f"%{name}%")).all()

# ✅ Delete a user by ID
def set_user_status(db: Session, user_id: int, status: bool):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.user_status = status
        db.commit()
        db.refresh(user)
    return user

def get_or_create_google_user(db: Session, email: str, name: str, token: str):
    user = db.query(User).filter(User.user_email == email).first()

    if user:
        user.token = token
        user.signed_method = "Google"
        user.user_status = True
        db.commit()
        db.refresh(user)
        return user

    user = User(
        user_email=email,
        user_name=name,
        user_status=True,
        signed_at=date.today(),
        signed_method="Google",
        token=token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# Get or create Facebook user
def get_or_create_facebook_user(db: Session, email: str, name: str, token: str):
    user = db.query(User).filter_by(user_email=email).first()
    if user:
        user.token = token
        user.signed_method = "Facebook"
        user.user_status = True
        db.commit()
        db.refresh(user)
        return user

    user = User(
        user_email=email,
        user_name=name,
        user_status=True,
        signed_at=date.today(),
        signed_method="Facebook",
        token=token,
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

# Get only contact info for user
def get_user_contact_info(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    return user  # We return the whole user object, Pydantic will filter fields

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    code = Column(String)
    expires_at = Column(DateTime)

#************************************** Admin Section *****************************************#

# Custom admin output with joins + formatting
def get_admin_users(db: Session):
    users = db.query(User).all()
    data = []

    for user in users:
        orders = db.query(OrderTable).filter(OrderTable.user_id == user.user_id).all()
        total_spent = sum([order.total_price or 0 for order in orders])
        order_count = len(orders)
        last_order = max([o.order_date for o in orders], default=None)

        data.append({
            "id": user.user_id,
            "name": user.user_name,
            "email": user.user_email,
            "phone": user.phone_number,
            "location": user.address,
            "orders": order_count,
            "spent": total_spent,
            "lastOrder": last_order,
            "status": 1 if user.user_status else 0,
            "avatar": user.photo,
            "signed_at": user.signed_at,
        })

    return data

# Set user status using 1 or 0
def set_user_status(db: Session, user_id: int, status: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    user.user_status = bool(status)  # 1 → True, 0 → False
    db.commit()
    db.refresh(user)
    return user

def get_customer_join_for_month(db: Session, year: int, month: int) -> int:
    
    count = db.query(func.count(User.user_id))\
              .filter(extract("month", OrderTable.order_date) == month)\
              .filter(extract("year", OrderTable.order_date) == year)\
              .scalar()
    return count or 0