from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import product_db, product_schema
from .attachment_product_db import get_attachments_by_product_id
from .product_schema import ProductCount
from datetime import date

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Add new product
@router.post("/NewProduct", response_model=product_schema.ProductOut)
def add_product(product: product_schema.ProductCreate, db: Session = Depends(get_db)):
    return product_db.create_product(db, product)

#  Get all products ✅
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

@router.get("/num_of_product", response_model=ProductCount)
def number_of_products_DB(db: Session = Depends(get_db)):
    number = product_db.get_number_of_products(db)
    return ProductCount(numberOfProducts=number)

######################################################################################################################333

@router.get("/top-selling-products", response_model=list[product_schema.TopSellingProduct])
def top_selling_products(db: Session = Depends(get_db)):
    products = product_db.get_top_selling_products(db)
    if not products:
        raise HTTPException(status_code=404, detail="No orders found.")
    return products    

@router.get("/all-products", response_model=list[product_schema.ProductWithDetails])
def fetch_all_products_with_details(db: Session = Depends(get_db)):
    products = product_db.get_all_products_with_details(db)
    if not products:
        raise HTTPException(status_code=404, detail="No products found.")
    return products
######################################################################################################################333
#  Get product by ID (with photo URLs)
@router.get("/{product_id}", response_model=product_schema.ProductOutWithDetails)
def fetch_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = product_db.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Attachments can still be added if needed
    product.attachments = get_attachments_by_product_id(db, product_id)
    return product
#  DELETE a product by ID
@router.delete("/{product_id}")
def delete_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = product_db.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": f"Product with ID {product_id} deleted successfully"}

