from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.order.TrackOrder_db import get_latest_tracking
from models.order.order_db import get_order_by_order_id
from models.order.TrackOrder_schema import TrackSummaryOut
from models.order.TrackOrder_schema import TrackInSimple
from models.order.TrackOrder_db import insert_tracking_entry
from models.order.TrackOrder_db import get_tracking_history
from models.order.TrackOrder_schema import TrackHistoryOut

from typing import List

router = APIRouter(prefix="/tracking", tags=["Tracking"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary/{order_id}", response_model=TrackSummaryOut)
def get_tracking_summary(order_id: int, db: Session = Depends(get_db)):
    order = get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    track = get_latest_tracking(db, order_id)
    current_location = track.location if track else None

    return TrackSummaryOut(
        order_id=order["order_id"],
        order_status=order["order_status"],
        tracking_number=order["tracking_number"],
        estimated_delivery=order["estimated_delivery"],
        origin_location="Ramallah",  # ثابت أو من إعدادات
        going_location=order["going_location"],
        current_location=current_location
    )


@router.post("/new-track")
def create_tracking_entry(track_data: TrackInSimple, db: Session = Depends(get_db)):
    try:
        entry = insert_tracking_entry(db, track_data)
        return {"message": "Tracking entry added", "track_id": entry.track_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert tracking: {str(e)}")
    


@router.get("/history/{order_id}", response_model=List[TrackHistoryOut])
def get_order_tracking_history(order_id: int, db: Session = Depends(get_db)):
    history = get_tracking_history(db, order_id)
    if not history:
        raise HTTPException(status_code=404, detail="No tracking history found for this order.")
    return history
