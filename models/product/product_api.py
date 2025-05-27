from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import product_db, product_schema
from .attachment_product_db import get_attachments_by_product_id
from .product_schema import ProductCount
from datetime import date

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Add new product
@router.post("/NewProduct", response_model=product_schema.ProductOut)
def add_product(product: product_schema.ProductCreate, db: Session = Depends(get_db)):
    return product_db.create_product(db, product)

#  Get all products ✅
@router.get("/", response_model=list[product_schema.ProductOut])
def fetch_all_products(db: Session = Depends(get_db)):
    products = product_db.get_all_products(db)
    output = []
    for p in products:
        attachments = get_attachments_by_product_id(db, p.product_id)
        out = product_schema.ProductOut.from_orm(p)
        out.attachments = attachments
        output.append(out)
    return output

@router.get("/num_of_product", response_model=ProductCount)
def number_of_products_DB(db: Session = Depends(get_db)):
    number = product_db.get_number_of_products(db)
    return ProductCount(numberOfProducts=number)

######################################################################################################################333

@router.get("/top-selling-products", response_model=list[product_schema.TopSellingProduct])
def top_selling_products(db: Session = Depends(get_db)):
    products = product_db.get_top_selling_products(db)
    if not products:
        raise HTTPException(status_code=404, detail="No orders found.")
    return products    

@router.get("/product-analytics", response_model=product_schema.ProductAnalytics)
def get_product_analytics(db: Session = Depends(get_db)):
    # Monthly analytics
    monthly_sales = product_db.get_total_product_sales_monthly(db)
    monthly_products_sold = product_db.get_num_of_products_sold_monthly(db)
    monthly_avg_price = product_db.get_avg_price_of_products_monthly(db)
    monthly_profit_margin = product_db.get_profit_margin_of_products_monthly(db)

    # Last 3 months analytics
    three_months_sales = product_db.get_total_product_sales_3month(db)
    three_months_products_sold = product_db.get_num_of_products_sold_3month(db)
    three_months_avg_price = product_db.get_avg_price_of_products_3month(db)
    three_months_profit_margin = product_db.get_profit_margin_of_products_3month(db)

    # Yearly analytics
    yearly_sales = product_db.get_total_product_sales_yearly(db)
    yearly_products_sold = product_db.get_num_of_products_sold_yearly(db)
    yearly_avg_price = product_db.get_avg_price_of_products_yearly(db)
    yearly_profit_margin = product_db.get_profit_margin_of_products_yearly(db)

    return product_schema.ProductAnalytics(
        # Monthly data
        current_month_sales=monthly_sales["current_month_sales"],
        previous_month_sales=monthly_sales["previous_month_sales"],
        current_month_products_sold=monthly_products_sold["current_month_products_sold"],
        previous_month_products_sold=monthly_products_sold["previous_month_products_sold"],
        current_month_avg_price=monthly_avg_price["current_month_avg_price"],
        previous_month_avg_price=monthly_avg_price["previous_month_avg_price"],
        current_month_profit_margin=monthly_profit_margin["current_month_profit_margin"],
        previous_month_profit_margin=monthly_profit_margin["previous_month_profit_margin"],

        # Last 3 months data
        last_three_months_sales=three_months_sales["last_three_months_sales"],
        previous_three_months_sales=three_months_sales["previous_three_months_sales"],
        last_three_months_products_sold=three_months_products_sold["last_three_months_products_sold"],
        previous_three_months_products_sold=three_months_products_sold["previous_three_months_products_sold"],
        last_three_months_avg_price=three_months_avg_price["last_three_months_avg_price"],
        previous_three_months_avg_price=three_months_avg_price["previous_three_months_avg_price"],
        last_three_months_profit_margin=three_months_profit_margin["last_three_months_profit_margin"],
        previous_three_months_profit_margin=three_months_profit_margin["previous_three_months_profit_margin"],

        # Yearly data
        current_year_sales=yearly_sales["current_year_sales"],
        previous_year_sales=yearly_sales["previous_year_sales"],
        current_year_products_sold=yearly_products_sold["current_year_products_sold"],
        previous_year_products_sold=yearly_products_sold["previous_year_products_sold"],
        current_year_avg_price=yearly_avg_price["current_year_avg_price"],
        previous_year_avg_price=yearly_avg_price["previous_year_avg_price"],
        current_year_profit_margin=yearly_profit_margin["current_year_profit_margin"],
        previous_year_profit_margin=yearly_profit_margin["previous_year_profit_margin"]
    )

@router.get("/top-performing-products", response_model=product_schema.TopPerformingProducts)
def get_top_performing_products(db: Session = Depends(get_db)):
    # Get top-performing products for monthly, 3-month, and yearly periods
    monthly_data = product_db.get_top_performing_products_monthly(db)
    three_months_data = product_db.get_top_performing_products_3month(db)
    yearly_data = product_db.get_top_performing_products_yearly(db)

    # Return the combined data
    return product_schema.TopPerformingProducts(
        monthly=[
            product_schema.ProductPerformance(
                product_name=item["product_name"],
                sales=item.get("current_month_sales", 0),
                units_sold=item.get("current_month_units_sold", 0),
                units_sold_growth_percentage=item.get("units_sold_growth_percentage", 0),
            )
            for item in monthly_data
        ],
        three_months=[
            product_schema.ProductPerformance(
                product_name=item["product_name"],
                sales=item.get("last_three_months_sales", 0),
                units_sold=item.get("last_three_months_units_sold", 0),
                units_sold_growth_percentage=item.get("units_sold_growth_percentage", 0),
            )
            for item in three_months_data
        ],
        yearly=[
            product_schema.ProductPerformance(
                product_name=item["product_name"],
                sales=item.get("current_year_sales", 0),
                units_sold=item.get("current_year_units_sold", 0),
                units_sold_growth_percentage=item.get("units_sold_growth_percentage", 0),
            )
            for item in yearly_data
        ],
    )
######################################################################################################################333

@router.get("/inventory-stats", response_model=product_schema.InventorySummary)
def inventory_summary_endpoint(db: Session = Depends(get_db)):
    return product_db.get_inventory_summary(db)

@router.get("/simple-products", response_model=list[product_schema.SimpleProductOut])
def get_all_simple_products(db: Session = Depends(get_db)):
    products = product_db.get_simple_products(db)
    return [product_schema.SimpleProductOut(**dict(row._mapping)) for row in products]

#  Get product by ID (with photo URLs)
@router.get("/{product_id}", response_model=product_schema.ProductOutWithDetails)
def fetch_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = product_db.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Attachments can still be added if needed
    product.attachments = get_attachments_by_product_id(db, product_id)
    return product
#  DELETE a product by ID
@router.delete("/{product_id}")
def delete_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = product_db.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": f"Product with ID {product_id} deleted successfully"}

