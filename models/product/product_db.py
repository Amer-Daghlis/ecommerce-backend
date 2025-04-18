from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from models.database import Base
from .product_schema import ProductCreate
from .attachment_product_db import get_attachments_by_product_id

class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    year_of_manufacturing = Column(Integer)
    original_price = Column(Float)
    selling_price = Column(Float)
    offer_percentage = Column(Float, default=0)
    total_quantity = Column(Integer)
    remaining_quantity = Column(Integer)
    product_rating = Column(Integer)
    number_of_users_rating_product = Column(Integer)
    availability_status = Column(Boolean)
    how_use_it = Column(String(255))
    category_id = Column(Integer, ForeignKey("category.category_id"))
    sub_category_id = Column(Integer, ForeignKey("sub_category.sub_category_id"))
    company_id = Column(Integer, ForeignKey("company.company_id"))
    added_at = Column(DateTime, default=datetime.utcnow)

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.product_id == product_id).first()
