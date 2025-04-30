from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import order_db, order_schema

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ GET: Number of orders by user_id
@router.get("/count/{user_id}", response_model=order_schema.UserOrderCount)
def get_user_order_count(user_id: int, db: Session = Depends(get_db)):
    count = order_db.get_user_order_count(db, user_id)
    return {
        "user_id": user_id,
        "order_count": count
    }

# ✅ GET: All orders for a specific user
@router.get("/user/{user_id}", response_model=list[order_schema.OrderOut])
def get_all_orders_for_user(user_id: int, db: Session = Depends(get_db)):
    orders = order_db.get_all_orders_for_user(db, user_id)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user.")
    return orders


#************************************** Admin Section *****************************************#

# Get the revenue for the current month
@router.get("/revenue/month", response_model=list[order_schema.MonthlyRevenue])
def get_monthly_and_previous_revenue(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()

    # Current month
    current_month = now.month
    current_year = now.year

    # Previous month logic
    if now.month == 1:
        previous_month = 12
        previous_year = now.year - 1
    else:
        previous_month = now.month - 1
        previous_year = now.year

    current_revenue = order_db.get_revenue_for_month(db, current_year, current_month)
    previous_revenue = order_db.get_revenue_for_month(db, previous_year, previous_month)

    return [
        {"month": current_month, "year": current_year, "total_revenue": current_revenue},
        {"month": previous_month, "year": previous_year, "total_revenue": previous_revenue}
    ]

#Get the total number of orders for the current month
@router.get("/orders-in-month", response_model=list[order_schema.MonthlyOrderCount])
def get_current_and_previous_month_order_counts(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()

    # Current month
    current_month = now.month
    current_year = now.year

    # Previous month logic
    if now.month == 1:
        previous_month = 12
        previous_year = now.year - 1
    else:
        previous_month = now.month - 1
        previous_year = now.year

    current_count = order_db.get_order_count_for_month(db, current_year, current_month)
    previous_count = order_db.get_order_count_for_month(db, previous_year, previous_month)

    return [
        {"month": current_month, "year": current_year, "total_orders": current_count},
        {"month": previous_month, "year": previous_year, "total_orders": previous_count}
    ]
# Get the total number of products bought in the current month
@router.get("/products-bought/month", response_model=list[order_schema.MonthlyProductsBought])
def get_products_bought_this_and_last_month(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()

    current_month = now.month
    current_year = now.year

    if now.month == 1:
        previous_month = 12
        previous_year = now.year - 1
    else:
        previous_month = now.month - 1
        previous_year = now.year

    current_count = order_db.get_products_bought_by_month(db, current_year, current_month)
    previous_count = order_db.get_products_bought_by_month(db, previous_year, previous_month)

    return [
        {
            "month": current_month,
            "year": current_year,
            "total_products_bought": current_count
        },
        {
            "month": previous_month,
            "year": previous_year,
            "total_products_bought": previous_count
        }
    ]


# Get the total number of customers who placed orders in the current month
@router.get("/customers/month", response_model=list[order_schema.MonthlyCustomerCount])
def get_customers_this_and_last_month(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()

    current_month = now.month
    current_year = now.year

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_data = order_db.get_customer_count_by_month(db, current_year, current_month)
    previous_data = order_db.get_customer_count_by_month(db, previous_year, previous_month)

    return [current_data, previous_data]
