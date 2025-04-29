from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ✅ Order response schema
class OrderOut(BaseModel):
    order_id: int
    user_id: int
    order_status: Optional[str]
    order_date: Optional[datetime]
    total_price: Optional[float]
    tracking_number: Optional[str]
    going_location: Optional[str]

    class Config:
        from_attributes = True  # Updated for Pydantic v2

# ✅ Order count response
class UserOrderCount(BaseModel):
    user_id: int
    order_count: int

    class Config:
        from_attributes = True  # Updated for Pydantic v2



#************************************** Admin Section *****************************************#


class MonthlyRevenue(BaseModel):
    month: int
    year: int
    total_revenue: float

    class Config:
        from_attributes = True


class MonthlyOrderCount(BaseModel):
    month: int
    year: int
    total_orders: int

    class Config:
        from_attributes = True

class MonthlyProductsBought(BaseModel):
    month: int
    year: int
    total_products_bought: int

    class Config:
        from_attributes = True
