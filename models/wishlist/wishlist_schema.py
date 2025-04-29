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

#  Wishlist count response
class UserWishlistCount(BaseModel):
    user_id: int
    wishlist_count: int

    class Config:
        from_attributes = True


# Get wishlist items for a user

#  Attachment schema (photos)
class ProductAttachmentOut(BaseModel):
    attachment_link: str

    class Config:
        orm_mode = True

# ✅ Full product schema for wishlist
class WishlistProductOut(BaseModel):
    product_id: int
    product_name: str
    product_rating: Optional[int]
    how_use_it: Optional[str]
    selling_price: float
    availability_status: Optional[bool]
    attachments: List[str] = []  # List of image links

    class Config:
        orm_mode = True

# ✅ Full user wishlist response
class UserWishlistOut(BaseModel):
    user_id: int
    wishlist: List[WishlistProductOut]

    class Config:
        orm_mode = True
        