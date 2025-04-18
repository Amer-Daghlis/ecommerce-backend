from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import product_db, product_schema
from .attachment_product_db import get_attachments_by_product_id

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🟢 Add new product
@router.post("/NewProduct", response_model=product_schema.ProductOut)
def add_product(product: product_schema.ProductCreate, db: Session = Depends(get_db)):
    return product_db.create_product(db, product)

# 🟡 Get all products
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

# 🔵 Get product by ID (with photo URLs)
@router.get("/{product_id}", response_model=product_schema.ProductOut)
def fetch_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = product_db.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    out = product_schema.ProductOut.from_orm(product)
    out.attachments = get_attachments_by_product_id(db, product_id)
    return out
# 🔴 DELETE a product by ID
@router.delete("/{product_id}")
def delete_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = product_db.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": f"Product with ID {product_id} deleted successfully"}
