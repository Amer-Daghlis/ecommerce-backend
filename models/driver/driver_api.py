from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .driver_db import get_all_drivers
from .driver_schema import DriverOut
from models.database import SessionLocal  # adjust to your actual DB session path
from .driver_db import get_all_delivery_orders
from .driver_schema import DeliveryOrderOut
router = APIRouter(prefix="/drivers", tags=["Drivers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[DriverOut])
def fetch_drivers(db: Session = Depends(get_db)):
    return get_all_drivers(db)

@router.get("/orders", response_model=list[DeliveryOrderOut])
def fetch_all_delivery_orders(db: Session = Depends(get_db)):
    return get_all_delivery_orders(db)
