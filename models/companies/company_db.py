from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, relationship
from models.database import Base

class Company(Base):
    __tablename__ = "company"

    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    company_phone = Column(String(20))
    location = Column(String(255))
    products = relationship("Product", back_populates="company")

def get_all_companies(db: Session):
    return db.query(Company).all()
