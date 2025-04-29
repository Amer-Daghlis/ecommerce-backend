from sqlalchemy import Column, Integer, Float, ForeignKey, func
from sqlalchemy.orm import Session
from models.database import Base
from models.product.product_db import Product
from models.product.attachment_product_db import AttachmentProduct
from models.companies.company_db import Company


class Cart(Base):
    __tablename__ = "cart"
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    total_price = Column(Float, default=0.0)


class CartProduct(Base):
    __tablename__ = "cart_product"
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    cart_id = Column(Integer, ForeignKey("cart.cart_id"), primary_key=True)
    quantity = Column(Float)


# 🔧 Ensure user has a cart (create if not exists)
def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id, total_price=0.0)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


# 🛒 Add a product to the user's cart
def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return None, "Product not found"

    cart = get_or_create_cart(db, user_id)

    existing = db.query(CartProduct).filter_by(cart_id=cart.cart_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartProduct(cart_id=cart.cart_id, product_id=product_id, quantity=quantity)
        db.add(item)

    cart.total_price += product.selling_price * quantity
    db.commit()
    return cart, None


# 📦 Get number of unique products in the user's cart
def get_cart_product_count(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        return 0  # No cart yet

    count = db.query(func.count(CartProduct.product_id))\
              .filter(CartProduct.cart_id == cart.cart_id)\
              .scalar()
    return count


def get_products_in_cart_by_cart_id(db: Session, cart_id: int):
    cart_products = (
        db.query(CartProduct, Product)
        .join(Product, CartProduct.product_id == Product.product_id)
        .filter(CartProduct.cart_id == cart_id)
        .all()
    )

    result = []
    for cart_product, product in cart_products:
        # Get brand name
        company = db.query(Company).filter(Company.company_id == product.company_id).first()
        brand = company.company_name if company else ""

        # Get first image
        image_obj = db.query(AttachmentProduct).filter(AttachmentProduct.product_id == product.product_id).first()
        image_url = image_obj.attachment_link if image_obj else ""

        result.append({
            "id": product.product_id,
            "name": product.product_name,
            "price": product.selling_price,
            "quantity": cart_product.quantity,  # ✅ from CartProduct
            "brand": brand,
            "discount": product.offer_percentage or 0,
            "quantityAvailable": product.remaining_quantity,
            "image": image_url
        })

    return result
