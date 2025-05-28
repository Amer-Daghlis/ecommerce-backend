from sqlalchemy.orm import Session

def update_order_status(db: Session, order_id: int, new_status: str):
    from models.order.order_db import OrderTable  # ✅ import محلي لحل الحلقة
    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    if order:
        order.order_status = new_status
        db.commit()
        db.refresh(order)
