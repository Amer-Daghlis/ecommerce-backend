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

class TrackTable(Base):
    __tablename__ = "traking_order"

    track_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("OrderTable.order_id"))
    order_status = Column(String(50))
    order_date = Column(Date)
    location = Column(String(50))
    description = Column(String(255))
    order = relationship("OrderTable", back_populates="tracking")

def set_order_tracking(db: Session, order_id: int, status: str, order_date: date, location: str, description: str = None):
    print(f"Setting tracking for order_id: {order_id}, status: {status}, order_date: {order_date}, location: {location}, description: {description}")
    new_track = TrackTable(
        order_id=order_id,
        order_status=status,
        order_date=order_date,
        location=location,
        description=description
    )
    db.add(new_track)
    db.commit()
    db.refresh(new_track)