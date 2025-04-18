from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import cart_schema, cart_db

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Add product to user's cart ✅
@router.post("/add")
def add_product_to_cart(data: cart_schema.AddToCartRequest, db: Session = Depends(get_db)):
    cart, error = cart_db.add_to_cart(db, data.user_id, data.product_id, data.quantity)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"message": "Product added to cart", "cart_id": cart.cart_id, "total_price": cart.total_price}
