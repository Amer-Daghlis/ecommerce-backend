from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, relationship
from models.database import Base
from sqlalchemy.sql.expression import func
from models.product.product_db import Product
from models.product.attachment_product_db import get_attachments_by_product_id
from sqlalchemy import func as sqlalchemy_func
from models.companies.company_db import Company  

class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), nullable=False)

    # 🔗 Relationship to product table
    products = relationship("Product", back_populates="category")

# ✅ Get all categories
def get_all_categories(db: Session):
    from sqlalchemy import func as sqlalchemy_func

    categories = db.query(Category).all()
    result = []

    for category in categories:
        product_count = db.query(sqlalchemy_func.count(Product.product_id))\
                          .filter(Product.category_id == category.category_id)\
                          .scalar()

        result.append({
            "category_id": category.category_id,
            "category_name": category.category_name,
            "description": getattr(category, "description", None),
            "photo": getattr(category, "photo", None),
            "product_count": product_count
        })

    return result


# ✅ Get 4 random categories with full fields
def get_random_categories(db: Session, limit: int = 4):
    categories = db.query(Category).order_by(func.rand()).limit(limit).all()
    result = []

    for category in categories:
        product_count = db.query(sqlalchemy_func.count(Product.product_id))\
                          .filter(Product.category_id == category.category_id)\
                          .scalar()

        result.append({
            "category_id": category.category_id,
            "category_name": category.category_name,
            "description": getattr(category, "description", None),
            "photo": getattr(category, "photo", None),
            "product_count": product_count
        })

    return result

# ✅ Get categories with full product info
def get_categories_with_products(db: Session):
    categories = db.query(Category).all()
    for category in categories:
        for product in category.products:
            product.attachments = get_attachments_by_product_id(db, product.product_id)
    return categories

# ✅ Get 4 random categories with product count
def get_random_categories_with_product_count(db: Session, limit: int = 4):
    categories = db.query(Category).order_by(func.rand()).limit(limit).all()
    result = []

    for category in categories:
        count = db.query(sqlalchemy_func.count(Product.product_id))\
                  .filter(Product.category_id == category.category_id).scalar()
        result.append({
            "category_id": category.category_id,
            "category_name": category.category_name,
            "product_count": count
        })

    return result

# ✅ NEW: Get simplified tools-only format for categories
def get_categories_with_tools_only(db: Session):
    categories = db.query(Category).all()
    output = []

    for category in categories:
        tools = []
        for p in category.products:
            company_name = None
            if p.company_id:
                company = db.query(Company).filter(Company.company_id == p.company_id).first()
                company_name = company.company_name if company else None

            tools.append({
                "product_id": p.product_id,
                "product_name": p.product_name,
                "selling_price": p.selling_price,
                "company_name": company_name,
                "description": p.how_use_it,
                "product_rating": p.product_rating,
                "availability_status": p.availability_status,
                "attachments": get_attachments_by_product_id(db, p.product_id)
            })

        output.append({
            "category_id": category.category_id,
            "category_name": category.category_name,
            "products": tools
        })

    return output

def get_top5_performance_categories_monthly(db: Session):
    from models.order.order_db import OrderProduct, OrderTable
    from models.product.product_db import Product
    from datetime import datetime
    from sqlalchemy import extract

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    category_performance = db.query(
        Category.category_name,
        func.count(Product.product_id).label("number_of_products"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("total_sales"),
        func.sum(OrderProduct.quantity * (Product.selling_price - Product.original_price)).label("total_profit")
    ).join(
        Product, Product.category_id == Category.category_id
    ).join(
        OrderProduct, Product.product_id == OrderProduct.product_id
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).filter(
        extract("year", OrderTable.order_date) == current_year,
        extract("month", OrderTable.order_date) == current_month
    ).group_by(
        Category.category_id
    ).order_by(
        func.sum(OrderProduct.quantity * Product.selling_price).desc()
    ).limit(5).all()

    # Format the result
    result = [
        {
            "category_name": row.category_name,
            "number_of_products": row.number_of_products,
            "total_sales": row.total_sales if row.total_sales else 0,
            "total_profit": row.total_profit if row.total_profit else 0
        }
        for row in category_performance
    ]

    return result

def get_top5_performance_categories_3month(db: Session):
    from models.order.order_db import OrderProduct, OrderTable
    from models.product.product_db import Product
    from datetime import datetime
    from sqlalchemy import extract, tuple_

    # Get the current date
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    last_three_months = [(current_year, current_month - i) if current_month - i > 0 else (current_year - 1, 12 + (current_month - i)) for i in range(3)]

    category_performance = db.query(
        Category.category_name,
        func.count(Product.product_id).label("number_of_products"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("total_sales"),
        func.sum(OrderProduct.quantity * (Product.selling_price - Product.original_price)).label("total_profit")
    ).join(
        Product, Product.category_id == Category.category_id
    ).join(
        OrderProduct, Product.product_id == OrderProduct.product_id
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).filter(
        tuple_(
            extract("year", OrderTable.order_date),
            extract("month", OrderTable.order_date)
        ).in_(last_three_months)
    ).group_by(
        Category.category_id
    ).order_by(
        func.sum(OrderProduct.quantity * Product.selling_price).desc()
    ).limit(5).all()

    # Format the result
    result = [
        {
            "category_name": row.category_name,
            "number_of_products": row.number_of_products,
            "total_sales": row.total_sales if row.total_sales else 0,
            "total_profit": row.total_profit if row.total_profit else 0
        }
        for row in category_performance
    ]

    return result

def get_top5_performance_categories_yearly(db: Session):
    from models.order.order_db import OrderProduct, OrderTable
    from models.product.product_db import Product
    from datetime import datetime
    from sqlalchemy import extract

    today = datetime.today()
    current_year = today.year

    category_performance = db.query(
        Category.category_name,
        func.count(Product.product_id).label("number_of_products"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("total_sales"),
        func.sum(OrderProduct.quantity * (Product.selling_price - Product.original_price)).label("total_profit")
    ).join(
        Product, Product.category_id == Category.category_id
    ).join(
        OrderProduct, Product.product_id == OrderProduct.product_id
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).filter(
        extract("year", OrderTable.order_date) == current_year
    ).group_by(
        Category.category_id
    ).order_by(
        func.sum(OrderProduct.quantity * Product.selling_price).desc()
    ).limit(5).all()

    # Format the result
    result = [
        {
            "category_name": row.category_name,
            "number_of_products": row.number_of_products,
            "total_sales": row.total_sales if row.total_sales else 0,
            "total_profit": row.total_profit if row.total_profit else 0
        }
        for row in category_performance
    ]

    return result