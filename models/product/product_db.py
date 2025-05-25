from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date, func
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from models.database import Base
from .product_schema import ProductCreate
from .attachment_product_db import get_attachments_by_product_id
from datetime import date

class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    year_of_manufacture = Column(Integer)
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
    added_at = Column(Date)
    description = Column(String(1024), nullable=True)
    uses =  Column(String(1024), nullable=True)
    land_size =  Column(String(1024), nullable=True)
    order_products = relationship("OrderProduct", back_populates="product")
    category = relationship("Category", back_populates="products")
    company = relationship("Company", back_populates="products")




    

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_all_products(db: Session):
    from ..companies.company_db import Company
    

    result = db.query(
        Product,
        Company.company_name.label("company_name")
    ).join(
        Company, Product.company_id == Company.company_id
    ).all()

    products = []
    for product, company_name in result:
        product.company_name = company_name
        products.append(product)

    return products

def get_product_by_id(db: Session, product_id: int):
    from ..categories.category_db import Category
    from ..companies.company_db import Company

    result = db.query(
        Product,
        Category.category_name.label("category_name"),
        Company.company_name.label("company_name")
    ).join(
        Category, Product.category_id == Category.category_id
    ).join(
        Company, Product.company_id == Company.company_id
    ).filter(
        Product.product_id == product_id
    ).first()

    if result:
        product, category_name, company_name = result
        product.category_name = category_name
        product.company_name = company_name
        return product

    return None

def get_number_of_products(db: Session) -> int:
    return db.query(Product).count()


#************************************** Admin Section *****************************************#

def get_top_selling_products(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    from ..categories.category_db import Category

    result = db.query(
        Product.product_id,
        Product.product_name,
        Category.category_name,
        Product.selling_price,
        Product.remaining_quantity,
        Product.total_quantity,
        func.sum(OrderProduct.quantity).label("total_sold_quantity")
    ).join(
        OrderProduct, Product.product_id == OrderProduct.product_id
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Category, Product.category_id == Category.category_id
    ).group_by(
        Product.product_id, Product.product_name, Category.category_name,
        Product.selling_price, Product.remaining_quantity, Product.total_quantity
    ).order_by(
        func.sum(OrderProduct.quantity).desc()
    ).limit(10).all()
    
    top_selling_products = [
        {
            "product_id": product_id,
            "product_name": product_name,
            "category_name": category_name,
            "selling_price": selling_price,
            "remaining_quantity": remaining_quantity,
            "total_quantity": total_quantity,
            "total_sold_quantity": total_sold_quantity
        }
        for product_id, product_name, category_name, selling_price, remaining_quantity, total_quantity, total_sold_quantity in result
    ]

    return top_selling_products


def get_all_products_with_details(db: Session):
    from ..categories.category_db import Category
    from .attachment_product_db import AttachmentProduct

    result = db.query(
        Product.product_id,
        Product.product_name,
        Category.category_name,
        Product.selling_price,
        Product.remaining_quantity,
        AttachmentProduct.attachment_link
    ).join(
        Category, Product.category_id == Category.category_id
    ).outerjoin(
        AttachmentProduct, Product.product_id == AttachmentProduct.product_id
    ).all()

    products = [
        {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category_name": product.category_name,
            "selling_price": product.selling_price,
            "remaining_quantity": product.remaining_quantity,
            "attachment_link": product.attachment_link
        }
        for product in result
    ]

    return products
    
