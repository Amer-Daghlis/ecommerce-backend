from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, func
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()

class DeliveryMan(Base):
    __tablename__ = "delivery_man"

    delivery_id = Column(Integer, primary_key=True, index=True)
    delivery_name = Column(String(100), nullable=True)
    delivery_phone = Column(String(20), nullable=True)
    delivery_photo = Column(String(255), nullable=True)
    vehicle_id = Column(String(50), nullable=True)

def get_all_drivers(db: Session):
    return db.query(DeliveryMan.delivery_id, DeliveryMan.delivery_name).all()

class DeliveryOrder(Base):
    __tablename__ = "delivery_order"
    order_id = Column(Integer, primary_key=True)
    delivery_id = Column(Integer, ForeignKey("delivery_man.delivery_id"))

class OrderTable(Base):
    __tablename__ = "ordertable"
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    going_location = Column(String(255))
    order_date = Column(Date)
    order_status = Column(String(100))

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255))

class OrderProduct(Base):
    __tablename__ = "order_product"
    order_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, primary_key=True)

class Product(Base):
    __tablename__ = "product"
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255))

# Data function
def get_all_delivery_orders(db: Session):
    query = (
        db.query(
            DeliveryOrder.delivery_id,
            DeliveryOrder.order_id,
            User.user_name.label("customer_name"),
            OrderTable.going_location,
            func.group_concat(Product.product_name).label("products_name"),
            OrderTable.order_date,
            DeliveryMan.delivery_name.label("driver_name"),
            OrderTable.order_status
        )
        .join(OrderTable, DeliveryOrder.order_id == OrderTable.order_id)
        .join(User, User.user_id == OrderTable.user_id)
        .join(OrderProduct, OrderProduct.order_id == DeliveryOrder.order_id)
        .join(Product, Product.product_id == OrderProduct.product_id)
        .join(DeliveryMan, DeliveryMan.delivery_id == DeliveryOrder.delivery_id)
        .group_by(DeliveryOrder.delivery_id, DeliveryOrder.order_id)
    )
    return query.all()

