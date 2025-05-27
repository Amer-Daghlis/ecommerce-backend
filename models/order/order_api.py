from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import order_db, order_schema, order_product_db
from ..cart.cart_db import set_cart_empty
from .TrackOrder_db import set_order_tracking
from datetime import timedelta,date
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

     
# ✅ POST: Insert Order
@router.post("/insertDeliveryOrder")
def insertOrder(order: order_schema.orderCreate, db: Session = Depends(get_db)):
    from datetime import date, timedelta
    from models.cart.cart_db import get_cart_products, set_cart_empty
    from models.product.product_db import decrease_product_quantity
    from models.order.order_product_db import add_product_to_order
    from models.order.TrackOrder_db import set_order_tracking
    import uuid

    try:
        order_data = order.dict()
        order_data["order_status"] = "Order Placed"
        order_data["order_date"] = date.today()
        order_data["payment"] = False
        order_data["payment_method"] = "Delivery"
        order_data["estimated_delivery"] = date.today() + timedelta(days=3)
        order_data["tracking_number"] = f"TRK-{uuid.uuid4().hex[:8].upper()}"

        new_order = order_db.insert_onDelivery_order(db, order_data)

        # ✅ اجلب فقط CartProduct
        products = get_cart_products(db, order_data["user_id"])
        if not products:
            raise HTTPException(status_code=400, detail="Cart is empty")

        print("Products returned from get_cart_products:", products)
        print("Type of first item:", type(products[0]) if products else "None")

        for item in products:
            print("DEBUG:", type(item), item.product_id, item.quantity)  # تأكيد
            add_product_to_order(db, new_order.order_id, item.product_id, int(item.quantity))
            decrease_product_quantity(db, item.product_id, int(item.quantity))

        set_cart_empty(db, new_order.user_id)

        set_order_tracking(
            db=db,
            order_id=new_order.order_id,
            status="Order Placed",
            order_date=order_data["order_date"],
            location="Warehouse - Ramallah",
            description="Order has been placed and is being processed."
        )

        return {"status": True, "order_id": new_order.order_id}

    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order failed: {e}")



# ✅ POST: Add products to an order
@router.post("/add-products")
def add_products_to_order(data: order_schema.AddProductsToOrderRequest, db: Session = Depends(get_db)):
    added_items = []
    for product in data.products:
        try:
            item = order_product_db.add_product_to_order(db, data.order_id, product.product_id, product.quantity)
            added_items.append(item)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to add product {product.product_id} to order: {e}")
    return {"message": "Products added to order successfully", "added_items": added_items}

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

    return  [
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

@router.get("/last-3-orders", response_model=list[order_schema.LastOrderOut])
def get_last_3_orders(db: Session = Depends(get_db)):
    orders = order_db.get_last_3_orders(db)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found.")
    return orders

@router.get("/all-customers-orders", response_model=list[order_schema.OrderOut])
def get_all_customers_orders(db: Session = Depends(get_db)):
    orders = order_db.get_all_customer_order(db)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found.")
    return orders

@router.get("/sales-analytics", response_model=order_schema.SalesAnalytics)
def get_sales_analytics(db: Session = Depends(get_db)):
    revenue_data = order_db.total_revenue_all_products(db)
    avg_order_value_data = order_db.avg_order_value(db)
    total_orders_data = order_db.total_orders(db)
    conversion_rate_data = order_db.conversion_rate(db)

    return order_schema.SalesAnalytics(
        current_month_revenue=revenue_data["current_month_revenue"],
        previous_month_revenue=revenue_data["previous_month_revenue"],
        current_month_avg_order_value=avg_order_value_data["current_month_avg"],
        previous_month_avg_order_value=avg_order_value_data["previous_month_avg"],
        current_month_orders=total_orders_data["current_month_orders"],
        previous_month_orders=total_orders_data["previous_month_orders"],
        current_month_conversion_rate=conversion_rate_data["current_month_conversion_rate"],
        previous_month_conversion_rate=conversion_rate_data["previous_month_conversion_rate"]
    )

@router.get("/customer-orders/{user_id}", response_model=list[order_schema.CustomerOrderOut])
def get_orders_for_customer_endpoint(user_id: int, db: Session = Depends(get_db)):
    orders = order_db.get_orders_for_customer(db, user_id)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer.")
    return orders

@router.get("/customer-info-order/{order_id}", response_model=order_schema.CustomerInfoOrder)
def get_name_email_customer_order(order_id: int, db: Session = Depends(get_db)):
    customerInfo = order_db.get_customer_info_for_order(db, order_id)
    if not customerInfo:
        raise HTTPException(status_code=404, detail="Order not found.")
    return customerInfo

@router.get("/order-info/{order_id}", response_model=order_schema.orderInfo)
def get_name_email_customer_order(order_id: int, db: Session = Depends(get_db)):
    orderInfo = order_db.get_order_by_order_id(db, order_id)
    if not orderInfo:
        raise HTTPException(status_code=404, detail="Order not found.")
    return orderInfo

@router.get("/order-products/{order_id}", response_model=list[order_schema.ProductDetailsInOrder])
def get_all_products_in_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    products = order_db.getAllProductsInOrder(db, order_id)
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this order.")
    return products