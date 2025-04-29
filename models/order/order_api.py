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
@router.get("/revenue/month", response_model=order_schema.MonthlyRevenue)
def get_monthly_revenue(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()
    total = order_db.get_monthly_revenue(db)
    return {
        "month": now.month,
        "year": now.year,
        "total_revenue": total
    }

#Get the total number of orders for the current month
@router.get("/orders-in-month", response_model=order_schema.MonthlyOrderCount)
def get_monthly_order_count(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()
    count = order_db.get_monthly_order_count(db)
    return {
        "month": now.month,
        "year": now.year,
        "total_orders": count
    }

# Get the total number of products bought in the current month
@router.get("/products-bought/month")
def get_products_bought_this_month(db: Session = Depends(get_db)):
    return order_db.get_total_products_bought_this_month(db)

# Get the total number of customers who placed orders in the current month
@router.get("/customers/month")
def get_total_customers_this_month(db: Session = Depends(get_db)):
    return order_db.get_total_customers_this_month(db)
