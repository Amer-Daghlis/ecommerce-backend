from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, func
from sqlalchemy.orm import Session
from models.database import Base
from sqlalchemy import extract
from sqlalchemy import extract, func
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from models.database import Base
from models.order.order_product_db import OrderProduct
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from datetime import datetime


# ✅ OrderTable Model defined here to avoid circular import
class OrderTable(Base):
    __tablename__ = "OrderTable"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id"))
    order_status = Column(String(50))
    order_date = Column(Date)
    total_price = Column(Float)
    tracking_number = Column(String(50))
    going_location = Column(String(255))

# ✅ Get number of orders made by a user
def get_user_order_count(db: Session, user_id: int):
    count = db.query(func.count(OrderTable.order_id))\
              .filter(OrderTable.user_id == user_id)\
              .scalar()
    return count

# ✅ Get all orders for a specific user
def get_all_orders_for_user(db: Session, user_id: int):
    return db.query(OrderTable)\
             .filter(OrderTable.user_id == user_id)\
             .order_by(OrderTable.order_date.desc())\
             .all()


#************************************** Admin Section *****************************************#
# Total revenue for current month
def get_monthly_revenue(db: Session):
    from datetime import datetime
    now = datetime.now()

    revenue = db.query(func.sum(OrderTable.total_price))\
        .filter(extract("month", OrderTable.order_date) == now.month)\
        .filter(extract("year", OrderTable.order_date) == now.year)\
        .scalar()

    return revenue or 0.0  # Return 0 if None

# Get total number of orders for the current month
def get_monthly_order_count(db: Session):
    from datetime import datetime
    now = datetime.now()

    count = db.query(func.count(OrderTable.order_id))\
        .filter(extract("month", OrderTable.order_date) == now.month)\
        .filter(extract("year", OrderTable.order_date) == now.year)\
        .scalar()

    return count or 0  # Return 0 if None

# Get total number of products bought this month
def get_total_products_bought_this_month(db: Session):
    current_month = datetime.now().month
    current_year = datetime.now().year

    count = db.query(OrderProduct)\
              .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
              .filter(extract('month', OrderTable.order_date) == current_month)\
              .filter(extract('year', OrderTable.order_date) == current_year)\
              .count()

    return {"products_bought_this_month": count}


# Get count of distinct users who placed orders this month (with month name)
def get_total_customers_this_month(db: Session):
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    month_name = now.strftime("%B")  # e.g., "April"

    total_customers = db.query(func.count(func.distinct(OrderTable.user_id)))\
        .filter(extract('month', OrderTable.order_date) == current_month)\
        .filter(extract('year', OrderTable.order_date) == current_year)\
        .scalar()

    return {
        "month": month_name,
        "total_customers": total_customers
    }
