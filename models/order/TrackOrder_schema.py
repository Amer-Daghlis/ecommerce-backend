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