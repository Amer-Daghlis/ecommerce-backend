from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Session
from models.database import Base
from models.product.product_db import Product
from models.product.attachment_product_db import get_attachments_by_product_id

class Favorite(Base):
    __tablename__ = "favorite"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    added_at = Column(DateTime, server_default=func.now())

def add_to_wishlist(db: Session, user_id: int, product_id: int):
    existing = db.query(Favorite).filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return False, "Already in wishlist"
    item = Favorite(user_id=user_id, product_id=product_id)
    db.add(item)
    db.commit()
    return True, None

def get_user_wishlist(db: Session, user_id: int):
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    wishlist = []
    for fav in favorites:
        product = db.query(Product).filter(Product.product_id == fav.product_id).first()
        if product:
            product.attachments = get_attachments_by_product_id(db, product.product_id)
            wishlist.append(product)
    return wishlist

def remove_from_wishlist(db: Session, user_id: int, product_id: int):
    item = db.query(Favorite).filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return False, "Product not in wishlist"
    db.delete(item)
    db.commit()
    return True, None


#  Get number of wishlist items for a user
def get_user_wishlist_count(db: Session, user_id: int):
    return db.query(func.count(Favorite.product_id))\
             .filter(Favorite.user_id == user_id)\
             .scalar()


# Get all wishlist products for a user
def get_user_wishlist_products(db: Session, user_id: int):
    wishlist_items = db.query(Product)\
                       .join(Favorite, Product.product_id == Favorite.product_id)\
                       .filter(Favorite.user_id == user_id)\
                       .all()

    # Add attachments (photos) for each product
    for product in wishlist_items:
        product.attachments = get_attachments_by_product_id(db, product.product_id)
    return wishlist_items
