
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from models.database import Base

class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), nullable=False)

def get_all_categories(db: Session):
    return db.query(Category).all()
