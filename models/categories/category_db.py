from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, relationship
from models.database import Base
from sqlalchemy.sql.expression import func
from models.product.product_db import Product
from models.product.attachment_product_db import get_attachments_by_product_id

class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), nullable=False)

    # 🔗 Relationship to product table
    products = relationship("Product", backref="category")

# ✅ Get all categories
def get_all_categories(db: Session):
    return db.query(Category).all()

# ✅ Get 4 random categories
def get_random_categories(db: Session, limit: int = 4):
    return db.query(Category).order_by(func.rand()).limit(limit).all()

# ✅ Get categories with full products and photos
def get_categories_with_products(db: Session):
    categories = db.query(Category).all()
    for category in categories:
        for product in category.products:
            product.attachments = get_attachments_by_product_id(db, product.product_id)
    return categories
