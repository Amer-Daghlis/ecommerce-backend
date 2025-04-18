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
