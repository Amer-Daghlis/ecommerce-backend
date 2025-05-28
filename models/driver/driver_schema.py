from pydantic import BaseModel
from datetime import date

class DriverOut(BaseModel):
    delivery_id: int
    delivery_name: str

    class Config:
        from_attributes = True  # For Pydantic v2


class DeliveryOrderOut(BaseModel):
    delivery_id: int
    order_id: int
    customer_name: str
    going_location: str
    products_name: str
    order_date: date
    driver_name: str
    order_status: str

    class Config:
        from_attributes = True
