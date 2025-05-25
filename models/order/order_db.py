from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, func
from sqlalchemy.orm import Session
from models.database import Base
from sqlalchemy import extract
from sqlalchemy import extract, func
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from models.database import Base
from models.order.order_product_db import OrderProduct
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from .order_schema import orderCreate
from datetime import datetime, date, timedelta
from sqlalchemy.orm import relationship
from models.order.TrackOrder_db import TrackTable
# ✅ OrderTable Model defined here to avoid circular import
class OrderTable(Base):
    __tablename__ = "OrderTable"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    order_status = Column(String(50)) # "Order Placed", "Processing", "Shipped", "In Transit", "Out for Delivery", "Delivered"
    order_date = Column(Date)
    total_price = Column(Float)
    tracking_number = Column(String(50))
    going_location = Column(String(255))
    payment = Column(Boolean, nullable=False)
    payment_method = Column(String(255), nullable=False)
    estimated_delivery = Column(Date, nullable=False)
    number_product = Column(Integer, nullable=False)
    receiver_name = Column(String(255))
    user = relationship("User", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")
    tracking = relationship("TrackTable", back_populates="order")

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

# ✅ Insert order into db
def insert_onDelivery_order(db: Session, order_data: dict):

    new_order = OrderTable(
        user_id=order_data["user_id"],
        order_status=order_data["order_status"],
        order_date=order_data["order_date"],
        total_price=order_data["total_price"],
        tracking_number=order_data["tracking_number"],
        going_location=order_data["going_location"],
        payment=order_data["payment"],
        payment_method=order_data["payment_method"],
        estimated_delivery=order_data["estimated_delivery"],
        number_product=order_data["number_product"],
        receiver_name=order_data["receiver_name"],
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order
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

def get_last_3_orders(db: Session):
    from ..user.user_db import User

    result = db.query(
        OrderTable.order_id,
        OrderTable.order_status,
        OrderTable.total_price,
        User.user_name
    ).join(
        User, OrderTable.user_id == User.user_id
    ).order_by(
        OrderTable.order_date.desc()
    ).limit(3).all()

    orders = [
        {
            "order_id": order_id,
            "order_status": order_status,
            "total_price": total_price,
            "user_name": user_name
        }
        for order_id, order_status, total_price, user_name in result
    ]
    return orders

def get_orders_for_customer(db: Session, user_id: int):
    result = db.query(
        OrderTable.order_id,
        OrderTable.order_date,
        OrderTable.number_product,
        OrderTable.total_price,
        OrderTable.order_status
    ).filter(
        OrderTable.user_id == user_id
    ).order_by(
        OrderTable.order_date.desc()
    ).all()

    # Format the result as a list of dictionaries
    orders = [
        {
            "order_id": order.order_id,
            "order_date": order.order_date.strftime("%Y-%m-%d"),  # Format date as string
            "number_product": order.number_product,
            "total_price": order.total_price,
            "order_status": order.order_status
        }
        for order in result
    ]

    return orders

def get_all_customer_order(db: Session):
    from ..user.user_db import User
    from ..product.product_db import Product
    from ..order.order_product_db import OrderProduct

    result = db.query(
        OrderTable.order_id,
        User.user_name,
        OrderTable.order_date,
        OrderTable.total_price,
        OrderTable.order_status,
        OrderTable.payment,
        OrderTable.payment_method,
        OrderTable.number_product,
    ).join(
        User, OrderTable.user_id == User.user_id
    ).all()

    orders = []
    for order in result:
        products = db.query(
            Product.product_name,
            OrderProduct.quantity,
            Product.product_id,
            Product.offer_percentage
        ).join(
            Product, OrderProduct.product_id == Product.product_id
        ).filter(
            OrderProduct.order_id == order.order_id
        ).all()
        order_data = {
            "order_id": order.order_id,
            "user_name": order.user_name,
            "order_date": order.order_date,
            "total_price": order.total_price,
            "order_status": order.order_status,
            "payment": order.payment,
            "payment_method": order.payment_method,
            "number_product": order.number_product,
            "payment_method": order.payment_method,
            "products": [
                {
                    "product_name": product.product_name,
                    "quantity": product.quantity,
                    "product_id": product.product_id,
                    "offer_percentage": product.offer_percentage,
                }
                for product in products
            ]
        }
        orders.append(order_data)
    return orders

def get_customer_info_for_order(db: Session, order_id: int):
    from ..user.user_db import User

    result = db.query(
        User.user_name,
        User.user_email,
    ).join(
        OrderTable, User.user_id == OrderTable.user_id
    ).filter(
        OrderTable.order_id == order_id
    ).first()

    if result:
        return {
            "user_name": result.user_name,
            "user_email": result.user_email,
        }
    else:
        return None
    

def get_order_by_order_id(db: Session, order_id: int):
    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    if not order:
        return None
    return {
        "order_id": order.order_id,
        "order_status": order.order_status,
        "order_date": order.order_date,
        "total_price": order.total_price,
        "tracking_number": order.tracking_number,
        "going_location": order.going_location,
        "payment": order.payment,
        "payment_method": order.payment_method,
        "estimated_delivery": order.estimated_delivery,
        "receiver_name": order.receiver_name
    }

def getAllProductsInOrder(db: Session, order_id: int):
    from ..product.product_db import Product
    from ..order.order_product_db import OrderProduct
    from ..product.attachment_product_db import get_attachments_by_product_id
    result = db.query(
        Product.product_name,
        OrderProduct.quantity,
        Product.product_id,
        Product.offer_percentage,
        Product.selling_price

    ).join(
        OrderProduct, Product.product_id == OrderProduct.product_id
    ).filter(
        OrderProduct.order_id == order_id
    ).all()
    products = [
        {
            "product_name": product.product_name,
            "quantity": product.quantity,
            "product_id": product.product_id,
            "offer_percentage": product.offer_percentage,
            "selling_price": product.selling_price,
            "attachments": get_attachments_by_product_id(db, product.product_id)
        }
        for product in result
    ]
    return products