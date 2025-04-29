from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session
from models.database import Base

# ✅ Define the OrderProduct model for the association table
class OrderProduct(Base):
    __tablename__ = "order_product"

    order_id = Column(Integer, ForeignKey("OrderTable.order_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    # Optional: Define relationships (can be useful for joins or ORM navigation)
    # order = relationship("OrderTable", back_populates="products")
    # product = relationship("Product")

# ✅ Insert product into an order

def add_product_to_order(db: Session, order_id: int, product_id: int, quantity: int):
    item = OrderProduct(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# ✅ Get all products in a specific order

def get_products_by_order(db: Session, order_id: int):
    return db.query(OrderProduct).filter(OrderProduct.order_id == order_id).all()
