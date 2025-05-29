from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class OrderProductItem(BaseModel):
    product_id: int
    product_name: str
    attachments: List[str] = []
    price: float
    discount: float
    quantity: int

class OrderInfoOut(BaseModel):
    order_id: int
    order_date: date
    estimated_delivery: date
    going_location: str
    receiver_name: str
    tracking_number: str
    user_email: str
    user_id: int
    number_of_orders_by_user: int
    shipping_method: str
    total_cost: float
    payment: bool
    products: List[OrderProductItem]
    driver_name: Optional[str]
    vehicle_id: Optional[str]
    driver_phone: Optional[str]
    driver_avatar: Optional[str]

    class Config:
        from_attributes = True
