from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date, func, extract, tuple_
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from models.database import Base
from .product_schema import ProductCreate, SimpleProductOut
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




    
def decrease_product_quantity(db: Session, product_id: int, quantity: int):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product:
        if product.remaining_quantity is None:
            raise ValueError(f"Product {product_id} has no stock defined")
        if product.remaining_quantity >= quantity:
            product.remaining_quantity -= quantity
        else:
            raise ValueError(f"Not enough stock for product_id: {product_id}")
    else:
        raise ValueError(f"Product not found: {product_id}")


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
    

def get_total_product_sales_monthly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_month_sales = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .filter(extract("month", OrderTable.order_date) == current_month)\
        .scalar()

    previous_month_sales = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == previous_year)\
        .filter(extract("month", OrderTable.order_date) == previous_month)\
        .scalar()

    return {
        "current_month_sales": current_month_sales if current_month_sales else 0,
        "previous_month_sales": previous_month_sales if previous_month_sales else 0
    }

def get_num_of_products_sold_monthly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_month_products_sold = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .filter(extract("month", OrderTable.order_date) == current_month)\
        .scalar()

    previous_month_products_sold = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == previous_year)\
        .filter(extract("month", OrderTable.order_date) == previous_month)\
        .scalar()

    return {
        "current_month_products_sold": current_month_products_sold if current_month_products_sold else 0,
        "previous_month_products_sold": previous_month_products_sold if previous_month_products_sold else 0
    }

def get_avg_price_of_products_monthly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_month_avg_price = db.query(func.avg(OrderProduct.quantity * Product.selling_price))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .filter(extract("month", OrderTable.order_date) == current_month)\
        .scalar()

    previous_month_avg_price = db.query(func.avg(OrderProduct.quantity * Product.selling_price))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == previous_year)\
        .filter(extract("month", OrderTable.order_date) == previous_month)\
        .scalar()

    return {
        "current_month_avg_price": current_month_avg_price if current_month_avg_price else 0,
        "previous_month_avg_price": previous_month_avg_price if previous_month_avg_price else 0
    }

def get_profit_margin_of_products_monthly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_month_profit_margin = db.query(func.sum((OrderProduct.quantity * (Product.selling_price - Product.original_price))))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .filter(extract("month", OrderTable.order_date) == current_month)\
        .scalar()

    previous_month_profit_margin = db.query(func.sum((OrderProduct.quantity * (Product.selling_price - Product.original_price))))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == previous_year)\
        .filter(extract("month", OrderTable.order_date) == previous_month)\
        .scalar()

    return {
        "current_month_profit_margin": current_month_profit_margin if current_month_profit_margin else 0,
        "previous_month_profit_margin": previous_month_profit_margin if previous_month_profit_margin else 0
    }

def get_total_product_sales_3month(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    from sqlalchemy import extract
    from datetime import datetime

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    last_three_months = [(current_year, current_month - i) if current_month - i > 0 else (current_year - 1, 12 + (current_month - i)) for i in range(3)]

    previous_three_months = [(current_year, current_month - i - 3) if current_month - i - 3 > 0 else (current_year - 1, 12 + (current_month - i - 3)) for i in range(3)]

    # Query for the last three months
    last_three_months_sales = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(last_three_months)
        )\
        .scalar()

    previous_three_months_sales = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(previous_three_months)
        )\
        .scalar()

    return {
        "last_three_months_sales": last_three_months_sales if last_three_months_sales else 0,
        "previous_three_months_sales": previous_three_months_sales if previous_three_months_sales else 0
    }
    

def get_num_of_products_sold_3month(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    from sqlalchemy import extract
    from datetime import datetime

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    last_three_months = [(current_year, current_month - i) if current_month - i > 0 else (current_year - 1, 12 + (current_month - i)) for i in range(3)]

    previous_three_months = [(current_year, current_month - i - 3) if current_month - i - 3 > 0 else (current_year - 1, 12 + (current_month - i - 3)) for i in range(3)]

    # Query for the last three months
    last_three_months_products_sold = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(last_three_months)
        )\
        .scalar()

    previous_three_months_products_sold = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(previous_three_months)
        )\
        .scalar()

    return {
        "last_three_months_products_sold": last_three_months_products_sold if last_three_months_products_sold else 0,
        "previous_three_months_products_sold": previous_three_months_products_sold if previous_three_months_products_sold else 0
    }

def get_avg_price_of_products_3month(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    from sqlalchemy import extract
    from datetime import datetime

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    last_three_months = [(current_year, current_month - i) if current_month - i > 0 else (current_year - 1, 12 + (current_month - i)) for i in range(3)]

    previous_three_months = [(current_year, current_month - i - 3) if current_month - i - 3 > 0 else (current_year - 1, 12 + (current_month - i - 3)) for i in range(3)]

    # Query for the last three months
    last_three_months_avg_price = db.query(func.avg(OrderProduct.quantity * Product.selling_price))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(last_three_months)
        )\
        .scalar()

    previous_three_months_avg_price = db.query(func.avg(OrderProduct.quantity * Product.selling_price))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(previous_three_months)
        )\
        .scalar()

    return {
        "last_three_months_avg_price": last_three_months_avg_price if last_three_months_avg_price else 0,
        "previous_three_months_avg_price": previous_three_months_avg_price if previous_three_months_avg_price else 0
    }


def get_profit_margin_of_products_3month(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    from sqlalchemy import extract
    from datetime import datetime

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    last_three_months = [(current_year, current_month - i) if current_month - i > 0 else (current_year - 1, 12 + (current_month - i)) for i in range(3)]

    previous_three_months = [(current_year, current_month - i - 3) if current_month - i - 3 > 0 else (current_year - 1, 12 + (current_month - i - 3)) for i in range(3)]

    # Query for the last three months
    last_three_months_profit_margin = db.query(func.sum((OrderProduct.quantity * (Product.selling_price - Product.original_price))))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(last_three_months)
        )\
        .scalar()

    previous_three_months_profit_margin = db.query(func.sum((OrderProduct.quantity * (Product.selling_price - Product.original_price))))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(
            tuple_(
                extract("year", OrderTable.order_date),
                extract("month", OrderTable.order_date)
            ).in_(previous_three_months)
        )\
        .scalar()

    return {
        "last_three_months_profit_margin": last_three_months_profit_margin if last_three_months_profit_margin else 0,
        "previous_three_months_profit_margin": previous_three_months_profit_margin if previous_three_months_profit_margin else 0
    }

def get_total_product_sales_yearly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    today = datetime.today()
    current_year = today.year

    current_year_sales = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .scalar()

    previous_year_sales = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == current_year - 1)\
        .scalar()

    return {
        "current_year_sales": current_year_sales if current_year_sales else 0,
        "previous_year_sales": previous_year_sales if previous_year_sales else 0
    }

def get_num_of_products_sold_yearly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    today = datetime.today()
    current_year = today.year

    current_year_products_sold = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .scalar()

    previous_year_products_sold = db.query(func.sum(OrderProduct.quantity))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract("year", OrderTable.order_date) == current_year - 1)\
        .scalar()

    return {
        "current_year_products_sold": current_year_products_sold if current_year_products_sold else 0,
        "previous_year_products_sold": previous_year_products_sold if previous_year_products_sold else 0
    }

def get_avg_price_of_products_yearly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    today = datetime.today()
    current_year = today.year

    current_year_avg_price = db.query(func.avg(OrderProduct.quantity * Product.selling_price))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .scalar()

    previous_year_avg_price = db.query(func.avg(OrderProduct.quantity * Product.selling_price))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == current_year - 1)\
        .scalar()

    return {
        "current_year_avg_price": current_year_avg_price if current_year_avg_price else 0,
        "previous_year_avg_price": previous_year_avg_price if previous_year_avg_price else 0
    }
def get_profit_margin_of_products_yearly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    today = datetime.today()
    current_year = today.year

    current_year_profit_margin = db.query(func.sum((OrderProduct.quantity * (Product.selling_price - Product.original_price))))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == current_year)\
        .scalar()

    previous_year_profit_margin = db.query(func.sum((OrderProduct.quantity * (Product.selling_price - Product.original_price))))\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .join(Product, OrderProduct.product_id == Product.product_id)\
        .filter(extract("year", OrderTable.order_date) == current_year - 1)\
        .scalar()

    return {
        "current_year_profit_margin": current_year_profit_margin if current_year_profit_margin else 0,
        "previous_year_profit_margin": previous_year_profit_margin if previous_year_profit_margin else 0
    }


def get_top_performing_products_monthly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable

    # Get the current date
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    # Calculate the previous month and year
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    # Query for current month's product sales
    current_month_data = db.query(
        Product.product_name,
        func.sum(OrderProduct.quantity).label("units_sold"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("sales")
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Product, OrderProduct.product_id == Product.product_id
    ).filter(
        extract("year", OrderTable.order_date) == current_year,
        extract("month", OrderTable.order_date) == current_month
    ).group_by(
        Product.product_id
    ).all()

    # Query for previous month's product sales
    previous_month_data = db.query(
        Product.product_name,
        func.sum(OrderProduct.quantity).label("units_sold"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("sales")
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Product, OrderProduct.product_id == Product.product_id
    ).filter(
        extract("year", OrderTable.order_date) == previous_year,
        extract("month", OrderTable.order_date) == previous_month
    ).group_by(
        Product.product_id
    ).all()

    # Convert query results to dictionaries for easier comparison
    current_month_dict = {row.product_name: {"units_sold": row.units_sold, "sales": row.sales} for row in current_month_data}
    previous_month_dict = {row.product_name: {"units_sold": row.units_sold, "sales": row.sales} for row in previous_month_data}

    # Calculate growth percentage and prepare the result
    performance_data = []
    for product_name, current_data in current_month_dict.items():
        previous_data = previous_month_dict.get(product_name, {"units_sold": 0, "sales": 0})
        units_sold_growth = ((current_data["units_sold"] - previous_data["units_sold"]) / previous_data["units_sold"] * 100) if previous_data["units_sold"] > 0 else 100

        performance_data.append({
            "product_name": product_name,
            "current_month_sales": current_data["sales"],
            "current_month_units_sold": current_data["units_sold"],
            "units_sold_growth_percentage": units_sold_growth
        })

    return performance_data

def get_top_performing_products_3month(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable

    # Get the current date
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    # Calculate the last three months
    last_three_months = [(current_year, current_month - i) if current_month - i > 0 else (current_year - 1, 12 + (current_month - i)) for i in range(3)]

    # Calculate the previous three months
    previous_three_months = [(current_year, current_month - i - 3) if current_month - i - 3 > 0 else (current_year - 1, 12 + (current_month - i - 3)) for i in range(3)]

    # Query for the last three months' product sales
    last_three_months_data = db.query(
        Product.product_name,
        func.sum(OrderProduct.quantity).label("units_sold"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("sales")
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Product, OrderProduct.product_id == Product.product_id
    ).filter(
        tuple_(
            extract("year", OrderTable.order_date),
            extract("month", OrderTable.order_date)
        ).in_(last_three_months)
    ).group_by(
        Product.product_id
    ).all()

    # Query for the previous three months' product sales
    previous_three_months_data = db.query(
        Product.product_name,
        func.sum(OrderProduct.quantity).label("units_sold"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("sales")
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Product, OrderProduct.product_id == Product.product_id
    ).filter(
        tuple_(
            extract("year", OrderTable.order_date),
            extract("month", OrderTable.order_date)
        ).in_(previous_three_months)
    ).group_by(
        Product.product_id
    ).all()

    # Convert query results to dictionaries for easier comparison
    last_three_months_dict = {row.product_name: {"units_sold": row.units_sold, "sales": row.sales} for row in last_three_months_data}
    previous_three_months_dict = {row.product_name: {"units_sold": row.units_sold, "sales": row.sales} for row in previous_three_months_data}

    # Calculate growth percentage and prepare the result
    performance_data = []
    for product_name, current_data in last_three_months_dict.items():
        previous_data = previous_three_months_dict.get(product_name, {"units_sold": 0, "sales": 0})
        units_sold_growth = ((current_data["units_sold"] - previous_data["units_sold"]) / previous_data["units_sold"] * 100) if previous_data["units_sold"] > 0 else 100

        performance_data.append({
            "product_name": product_name,
            "last_three_months_sales": current_data["sales"],
            "last_three_months_units_sold": current_data["units_sold"],
            "units_sold_growth_percentage": units_sold_growth
        })

    return performance_data

def get_top_performing_products_yearly(db: Session):
    from ..order.order_db import OrderProduct
    from ..order.order_db import OrderTable
    from sqlalchemy import extract
    from datetime import datetime

    # Get the current date
    today = datetime.today()
    current_year = today.year

    # Query for the current year's product sales
    current_year_data = db.query(
        Product.product_name,
        func.sum(OrderProduct.quantity).label("units_sold"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("sales")
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Product, OrderProduct.product_id == Product.product_id
    ).filter(
        extract("year", OrderTable.order_date) == current_year
    ).group_by(
        Product.product_id
    ).all()

    # Query for the previous year's product sales
    previous_year_data = db.query(
        Product.product_name,
        func.sum(OrderProduct.quantity).label("units_sold"),
        func.sum(OrderProduct.quantity * Product.selling_price).label("sales")
    ).join(
        OrderTable, OrderProduct.order_id == OrderTable.order_id
    ).join(
        Product, OrderProduct.product_id == Product.product_id
    ).filter(
        extract("year", OrderTable.order_date) == current_year - 1
    ).group_by(
        Product.product_id
    ).all()

    # Convert query results to dictionaries for easier comparison
    current_year_dict = {row.product_name: {"units_sold": row.units_sold, "sales": row.sales} for row in current_year_data}
    previous_year_dict = {row.product_name: {"units_sold": row.units_sold, "sales": row.sales} for row in previous_year_data}

    # Calculate growth percentage and prepare the result
    performance_data = []
    for product_name, current_data in current_year_dict.items():
        previous_data = previous_year_dict.get(product_name, {"units_sold": 0, "sales": 0})
        units_sold_growth = ((current_data["units_sold"] - previous_data["units_sold"]) / previous_data["units_sold"] * 100) if previous_data["units_sold"] > 0 else 100

        performance_data.append({
            "product_name": product_name,
            "current_year_sales": current_data["sales"],
            "current_year_units_sold": current_data["units_sold"],
            "units_sold_growth_percentage": units_sold_growth
        })

    return performance_data


def get_inventory_summary(db: Session):
    # Total number of products
    total_products = db.query(func.count(Product.product_id)).scalar()

    # In stock (quantity > 0)
    in_stock = db.query(func.count(Product.product_id)).filter(Product.remaining_quantity > 0).scalar()

    # Low stock (quantity < 10)
    low_stock_count = db.query(func.count(Product.product_id)).filter(Product.remaining_quantity < 10).scalar()

    # Inventory value = sum(remaining_quantity * selling_price)
    inventory_value = db.query(func.sum(Product.remaining_quantity * Product.selling_price)).scalar()

    return {
        "total_products": total_products or 0,
        "in_stock": in_stock or 0,
        "low_stock_count": low_stock_count or 0,
        "inventory_value": inventory_value or 0.0
    }



def get_all_simple_products(db: Session):
    from ..categories.category_db import Category
    from .attachment_product_db import get_attachments_by_product_id

    products = db.query(Product).all()
    output = []

    for product in products:
        category_name = db.query(Category.category_name).filter(Category.category_id == product.category_id).scalar()
        attachments = get_attachments_by_product_id(db, product.product_id)

        # ✅ Determine stock status
        if product.remaining_quantity is None:
            status = "Unknown"
        elif product.remaining_quantity == 0:
            status = "Out of Stock"
        elif product.remaining_quantity <= 10:
            status = "Low Stock"
        else:
            status = "In Stock"

        output.append({
            "product_id": product.product_id,
            "product_name": product.product_name,
            "original_price": product.original_price,
            "selling_price": product.selling_price,
            "remaining_quantity": product.remaining_quantity,
            "availability_status": status,
            "category_name": category_name or "",
            "attachments": attachments
        })

    return output

