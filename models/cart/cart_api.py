from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import cart_schema, cart_db

router = APIRouter(prefix="/cart", tags=["Cart"])

# 🔧 Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ POST: Add product to user's cart
@router.post("/add")
def add_product_to_cart(data: cart_schema.AddToCartRequest, db: Session = Depends(get_db)):
    cart, error = cart_db.add_to_cart(db, data.user_id, data.product_id, data.quantity)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {
        "message": "Product added to cart",
        "cart_id": cart.cart_id,
        "total_price": cart.total_price
    }


# ✅ GET: Get number of unique products in user's cart
@router.get("/count/{user_id}")
def get_cart_product_count(user_id: int, db: Session = Depends(get_db)):
    count = cart_db.get_cart_product_count(db, user_id)
    return {"user_id": user_id, "product_count": count}


@router.get("/products/{cart_id}")
def get_products_in_cart(cart_id: int, db: Session = Depends(get_db)):
    products = cart_db.get_products_in_cart_by_cart_id(db, cart_id)
    if not products:
        return {"message": "Cart is empty or not found."}
    return products
