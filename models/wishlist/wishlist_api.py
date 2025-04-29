from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import wishlist_schema, wishlist_db

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Add to Wishlist ✅
@router.post("/add")
def add_to_wishlist(data: wishlist_schema.AddToWishlistRequest, db: Session = Depends(get_db)):
    success, error = wishlist_db.add_to_wishlist(db, data.user_id, data.product_id)
    if not success:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Product added to wishlist successfully"}
#  GET wishlist for user ✅
@router.get("/{user_id}", response_model=list[wishlist_schema.WishlistItemOut])
def get_user_wishlist(user_id: int, db: Session = Depends(get_db)):
    return wishlist_db.get_user_wishlist(db, user_id)

#  DELETE from wishlist
@router.delete("/remove")
def remove_from_wishlist(data: wishlist_schema.AddToWishlistRequest, db: Session = Depends(get_db)):
    success, error = wishlist_db.remove_from_wishlist(db, data.user_id, data.product_id)
    if not success:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Product removed from wishlist successfully"}


#  GET: Number of wishlist items for a user
@router.get("/count/{user_id}", response_model=wishlist_schema.UserWishlistCount)
def get_user_wishlist_count(user_id: int, db: Session = Depends(get_db)):
    count = wishlist_db.get_user_wishlist_count(db, user_id)
    return {
        "user_id": user_id,
        "wishlist_count": count
    }

# GET: Get full wishlist products for user
@router.get("/user/{user_id}", response_model=wishlist_schema.UserWishlistOut)
def get_user_wishlist_products(user_id: int, db: Session = Depends(get_db)):
    wishlist = wishlist_db.get_user_wishlist_products(db, user_id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="No wishlist products found for this user.")
    
    products_out = [
        wishlist_schema.WishlistProductOut(
            product_id=product.product_id,
            product_name=product.product_name,
            product_rating=product.product_rating,
            how_use_it=product.how_use_it,
            selling_price=product.selling_price,
            availability_status=product.availability_status,
            attachments=product.attachments
        )
        for product in wishlist
    ]

    return {
        "user_id": user_id,
        "wishlist": products_out
    }
