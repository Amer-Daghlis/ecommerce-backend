from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AddToWishlistRequest(BaseModel):
    user_id: int
    product_id: int

class WishlistItemOut(BaseModel):
    product_id: int
    product_name: str
    year_of_manufacturing: Optional[int]
    original_price: Optional[float]
    selling_price: Optional[float]
    offer_percentage: Optional[float]
    total_quantity: Optional[int]
    remaining_quantity: Optional[int]
    product_rating: Optional[int]
    number_of_users_rating_product: Optional[int]
    availability_status: Optional[bool]
    how_use_it: Optional[str]
    category_id: Optional[int]
    sub_category_id: Optional[int]
    company_id: Optional[int]
    added_at: datetime
    attachments: List[str] = []

    class Config:
        orm_mode = True
