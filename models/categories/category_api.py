from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import category_db, category_schema

router = APIRouter(prefix="/categories", tags=["Categories"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  GET all categories
@router.get("/", response_model=list[category_schema.CategoryOut])
def get_all_categories(db: Session = Depends(get_db)):
    return category_db.get_all_categories(db)
