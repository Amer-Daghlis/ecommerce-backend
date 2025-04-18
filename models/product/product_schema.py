from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    product_name: str
    year_of_manufacturing: Optional[int] = None
    original_price: Optional[float] = None
    selling_price: Optional[float] = None
    offer_percentage: Optional[float] = 0
    total_quantity: Optional[int] = None
    remaining_quantity: Optional[int] = None
    product_rating: Optional[int] = None
    number_of_users_rating_product: Optional[int] = None
    availability_status: Optional[bool] = True
    how_use_it: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    company_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    product_id: int
    added_at: datetime
    attachments: List[str] = []

    class Config:
        from_attributes = True  # ✅ Required for `.from_orm()` in Pydantic v2+
