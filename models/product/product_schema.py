from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

class ProductBase(BaseModel):
    product_name: str
    year_of_manufacture: Optional[int] = None
    original_price: Optional[float] = None
    selling_price: Optional[float] = None
    offer_percentage: Optional[float] = 0
    total_quantity: Optional[int] = None
    remaining_quantity: Optional[int] = None
    product_rating: Optional[float] = None
    number_of_users_rating_product: Optional[int] = None
    availability_status: Optional[bool] = True
    how_use_it: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    company_id: Optional[int] = None
    added_at: Optional[date] = None
    description: Optional[str] = None
    uses: Optional[str] = None
    land_size: Optional[str] = None

class ProductCreate(ProductBase):
    attachments: List[str] = []

class ProductOut(ProductBase):
    product_id: int
    attachments: List[str] = []
    company_name: Optional[str] = None

    class Config:
        from_attributes = True  # ✅ Required for `.from_orm()` in Pydantic v2+

class ProductOutWithDetails(ProductOut):
    category_name: str
    company_name: str

class ProductCount(BaseModel):
    numberOfProducts: int


#************************************** Admin Section *****************************************#

class TopSellingProduct(BaseModel):
    product_id: int
    product_name: str
    category_name: str
    selling_price: float
    remaining_quantity: int
    total_quantity: int
    total_sold_quantity: int


    class Config:
        from_attributes = True  # ✅ Required for `.from_orm()` in Pydantic v2+


class ProductWithDetails(BaseModel):
    product_id: int
    product_name: str
    category_name: str
    selling_price: float
    remaining_quantity: int
    attachment_link: Optional[str]

    class Config:
        orm_mode = True
class ProductAnalytics(BaseModel):
    current_month_sales: float
    previous_month_sales: float
    current_month_products_sold: int
    previous_month_products_sold: int
    current_month_avg_price: float
    previous_month_avg_price: float
    current_month_profit_margin: float
    previous_month_profit_margin: float

    last_three_months_sales: float
    previous_three_months_sales: float
    last_three_months_products_sold: int
    previous_three_months_products_sold: int
    last_three_months_avg_price: float
    previous_three_months_avg_price: float
    last_three_months_profit_margin: float
    previous_three_months_profit_margin: float

    current_year_sales: float
    previous_year_sales: float
    current_year_products_sold: int
    previous_year_products_sold: int
    current_year_avg_price: float
    previous_year_avg_price: float
    current_year_profit_margin: float
    previous_year_profit_margin: float

    class Config:
        from_attributes = True

class ProductPerformance(BaseModel):
    product_name: str
    sales: float
    units_sold: int
    units_sold_growth_percentage: float
    class Config:
        from_attributes = True


class TopPerformingProducts(BaseModel):
    monthly: List[ProductPerformance]
    three_months: List[ProductPerformance]
    yearly: List[ProductPerformance]

    class Config:
        from_attributes = True

# for inventory summary
class InventorySummary(BaseModel):
    current_month_product_count: int
    previous_month_product_count: int
    current_month_quantity: int
    previous_month_quantity: int
    low_stock_count: int
    inventory_value: float

    class Config:
        from_attributes = True


class SimpleProductOut(BaseModel):
    product_id: int
    product_name: str
    original_price: Optional[float]
    selling_price: Optional[float]
    remaining_quantity: Optional[int]  # ✅ Show remaining, not total
    availability_status: str           # ✅ Custom status
    category_name: str
    attachments: List[str] = []

    class Config:
        from_attributes = True
