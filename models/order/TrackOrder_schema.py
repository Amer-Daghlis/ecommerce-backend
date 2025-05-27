from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List


class TrackIn(BaseModel):
    order_id: int
    order_status: str
    order_date: date
    location: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class TrackSummaryOut(BaseModel):
    order_id: int
    order_status: str
    tracking_number: str
    estimated_delivery: date
    origin_location: str  # ثابت مثلاً رام الله
    going_location: str
    current_location: Optional[str]

    class Config:
        from_attributes = True


class TrackInSimple(BaseModel):
    order_id: int
    order_status: str
    location: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
