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
def get_revenue_for_month(db: Session, year: int, month: int) -> float:
    revenue = db.query(func.sum(OrderTable.total_price))\
        .filter(extract("month", OrderTable.order_date) == month)\
        .filter(extract("year", OrderTable.order_date) == year)\
        .scalar()
    return revenue or 0.0


# Get total number of orders for the current month
def get_order_count_for_month(db: Session, year: int, month: int) -> int:
    count = db.query(func.count(OrderTable.order_id))\
              .filter(extract("month", OrderTable.order_date) == month)\
              .filter(extract("year", OrderTable.order_date) == year)\
              .scalar()
    return count or 0


# Get total number of products bought this month
def get_products_bought_by_month(db: Session, year: int, month: int) -> int:
    count = db.query(OrderProduct)\
        .join(OrderTable, OrderProduct.order_id == OrderTable.order_id)\
        .filter(extract('month', OrderTable.order_date) == month)\
        .filter(extract('year', OrderTable.order_date) == year)\
        .count()

    return count or 0


# Get count of distinct users who placed orders this month (with month name)
def get_customer_count_by_month(db: Session, year: int, month: int) -> dict:
    month_name = datetime(year, month, 1).strftime("%B")
    count = db.query(func.count(func.distinct(OrderTable.user_id)))\
        .filter(extract('month', OrderTable.order_date) == month)\
        .filter(extract('year', OrderTable.order_date) == year)\
        .scalar()
    return {
        "month": month_name,
        "total_customers": count or 0
    }
