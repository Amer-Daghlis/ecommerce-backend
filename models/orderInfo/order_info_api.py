from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from .order_info_db import get_order_info_by_order_id
from .order_info_schema import OrderInfoOut

router = APIRouter(prefix="/order-info", tags=["Order Info"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{order_id}", response_model=OrderInfoOut)
def fetch_order_info(order_id: int, db: Session = Depends(get_db)):
    result = get_order_info_by_order_id(db, order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result
