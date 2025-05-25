from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List

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

class orderCreate(BaseModel):
    user_id: int
    total_price: float
    tracking_number: str
    going_location: str
    number_product: int
    receiver_name: str

    class Config:
        from_attributes = True  # Updated for Pydantic v2

class ProductInOrder(BaseModel):
    product_id: int
    quantity: int

class AddProductsToOrderRequest(BaseModel):
    order_id: int
    products: List[ProductInOrder]

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


class MonthlyCustomerCount(BaseModel):
    month: str
    total_customers: int

    class Config:
        from_attributes = True

class LastOrderOut(BaseModel):
    order_id: int
    order_status: str
    total_price: float
    user_name: str

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    product_name: str
    quantity: int
    product_id: int  # ✅ Correct
    offer_percentage: float

class OrderOut(BaseModel):
    order_id: int
    user_name: str
    order_date: date
    total_price: float
    order_status: str
    payment: bool
    payment_method: str
    number_product: int
    products: List[ProductOut]

    class Config:
        orm_mode = True

class CustomerOrderOut(BaseModel):
    order_id: int
    order_date: datetime
    number_product: int
    total_price: float
    order_status: str

    class Config:
        orm_mode = True

class CustomerInfoOrder(BaseModel):
    user_name: str
    user_email: str

    class Config:
        from_attributes = True

class orderInfo(BaseModel):
    order_id: int
    order_status: Optional[str]
    order_date: Optional[datetime]
    total_price: Optional[float]
    tracking_number: Optional[str]
    going_location: Optional[str]
    receiver_name: str
    payment_method: str
    estimated_delivery: Optional[date]
    payment: bool

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class ProductAttachment(BaseModel):
    attachment_link: str


class ProductDetailsInOrder(BaseModel):
    product_name: str
    quantity: int
    product_id: int
    offer_percentage: Optional[float] = 0
    selling_price: float
    attachments: Optional[List[ProductAttachment]] = []

    class Config:
        orm_mode = True