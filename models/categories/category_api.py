from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import category_db, category_schema

router = APIRouter(prefix="/categories", tags=["Categories"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ GET all categories
@router.get("/", response_model=list[category_schema.CategoryOut])
def get_all_categories(db: Session = Depends(get_db)):
    return category_db.get_all_categories(db)

# ✅ GET 4 random categories
@router.get("/random", response_model=list[category_schema.CategoryOut])
def get_random_categories(db: Session = Depends(get_db)):
    return category_db.get_random_categories(db)

# ✅ GET all categories with full products
@router.get("/with-products", response_model=list[category_schema.CategoryWithProducts])
def get_categories_with_products(db: Session = Depends(get_db)):
    return category_db.get_categories_with_products(db)

# ✅ NEW: GET categories with tools (id, name, price, company, rating, desc, etc.)
@router.get("/with-tools", response_model=list[category_schema.CategoryWithTools])
def get_categories_with_tools(db: Session = Depends(get_db)):
    return category_db.get_categories_with_tools_only(db)

@router.get("/top-performance-categories", response_model=category_schema.TopPerformanceCategories)
def get_top_performance_categories(db: Session = Depends(get_db)):
    # Get top-performing categories for monthly, 3-month, and yearly periods
    monthly_data = category_db.get_top5_performance_categories_monthly(db)
    three_months_data = category_db.get_top5_performance_categories_3month(db)
    yearly_data = category_db.get_top5_performance_categories_yearly(db)

    # Return the combined data
    return category_schema.TopPerformanceCategories(
        monthly=[
            category_schema.CategoryPerformance(
                category_name=item["category_name"],
                number_of_products=item["number_of_products"],
                total_sales=item["total_sales"],
                total_profit=item["total_profit"]
            )
            for item in monthly_data
        ],
        three_months=[
            category_schema.CategoryPerformance(
                category_name=item["category_name"],
                number_of_products=item["number_of_products"],
                total_sales=item["total_sales"],
                total_profit=item["total_profit"]
            )
            for item in three_months_data
        ],
        yearly=[
            category_schema.CategoryPerformance(
                category_name=item["category_name"],
                number_of_products=item["number_of_products"],
                total_sales=item["total_sales"],
                total_profit=item["total_profit"]
            )
            for item in yearly_data
        ],
    )