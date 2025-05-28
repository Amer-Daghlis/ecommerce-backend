from fastapi import HTTPException
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
from .TrackOrder_schema import TrackInSimple  
from sqlalchemy import insert, table, column, Integer
from models.order.common import update_order_status
import traceback
import sys


class TrackTable(Base):
    __tablename__ = "traking_order"

    track_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("OrderTable.order_id"))
    order_status = Column(String(50))
    order_date = Column(Date)
    location = Column(String(50))
    description = Column(String(255))
    order = relationship("OrderTable", back_populates="tracking")


class DeliveryOrder(Base):
    __tablename__ = "delivery_order"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)        # ✅ بدون ForeignKey
    delivery_id = Column(Integer)     # ✅ بدون ForeignKey

class DeliveryMan(Base):
    __tablename__ = "delivery_man"

    delivery_id = Column(Integer, primary_key=True)
    # باقي الحقول...
    name = Column(String(50))

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

def get_latest_tracking(db: Session, order_id: int):
    return db.query(TrackTable)\
             .filter(TrackTable.order_id == order_id)\
             .order_by(TrackTable.order_date.desc())\
             .first()


def insert_tracking_entry(db: Session, data: TrackInSimple):
    from datetime import date
    from models.order.common import update_order_status
    import traceback, sys

    try:
        print("🚀 Start insert_tracking_entry")
        print("🟡 Data:", data)

        # 🟢 إنشاء سجل التتبع الجديد
        new_track = TrackTable(
            order_id=data.order_id,
            order_status=data.order_status,
            order_date=date.today(),
            location=data.location,
            description=data.description
        )
        db.add(new_track)

        # 🟢 تحديث حالة الطلب
        update_order_status(db, data.order_id, data.order_status)

        # 🟢 إضافة العلاقة مع المندوب إذا موجود delivery_id
        if data.delivery_id is not None:
            existing_entry = db.query(DeliveryOrder).filter_by(
                order_id=data.order_id,
                delivery_id=data.delivery_id
            ).first()

            if not existing_entry:
                delivery_entry = DeliveryOrder(
                    order_id=data.order_id,
                    delivery_id=data.delivery_id
                )
                db.add(delivery_entry)
                print("✅ Delivery link added.")
            else:
                print("⚠️ Delivery link already exists. Skipping insert.")

        # 🟢 تأكيد الحفظ
        db.commit()
        db.refresh(new_track)
        print("✅ Tracking entry inserted successfully.")
        return new_track

    except Exception as e:
        db.rollback()
        print("🔴 ERROR TRACE:")
        traceback.print_exc(file=sys.stdout)
        raise HTTPException(status_code=500, detail=f"Failed to insert tracking: {e}")



def get_tracking_history(db: Session, order_id: int):
    return db.query(TrackTable)\
             .filter(TrackTable.order_id == order_id)\
             .order_by(TrackTable.order_date.asc())\
             .all()

