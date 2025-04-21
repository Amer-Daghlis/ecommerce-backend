from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CategoryOut(BaseModel):
    category_id: int
    category_name: str
    description: Optional[str] = None
    photo: Optional[str] = None
    product_count: int

    class Config:
        orm_mode = True

# 🔽 Attachment schema for product photos
class ProductAttachmentOut(BaseModel):
    attachment_link: str

    class Config:
        orm_mode = True

# 🔽 Full product info with photo URLs
class ProductOut(BaseModel):
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

# 🔽 Category with full product list
class CategoryWithProducts(BaseModel):
    category_id: int
    category_name: str
    products: List[ProductOut] = []

    class Config:
        orm_mode = True

# 🔽 Random category with product count
class CategoryWithProductCount(BaseModel):
    category_id: int
    category_name: str
    product_count: int

    class Config:
        orm_mode = True

# ✅ New: Tool-focused product schema
class ToolProductOut(BaseModel):
    product_id: int
    product_name: str
    selling_price: Optional[float]
    company_name: Optional[str]
    description: Optional[str]
    product_rating: Optional[int]
    availability_status: Optional[bool]
    attachments: List[str] = []

    class Config:
        orm_mode = True


# ✅ New: Category with tools only
class CategoryWithTools(BaseModel):
    category_id: int
    category_name: str
    products: List[ToolProductOut] = []

    class Config:
        orm_mode = True
