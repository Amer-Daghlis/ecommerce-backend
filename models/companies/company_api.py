from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import SessionLocal
from . import company_db, company_schema

router = APIRouter(prefix="/companies", tags=["Companies"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Return only company names
@router.get("/", response_model=list[company_schema.CompanyNameOut])
def get_all_company_names(db: Session = Depends(get_db)):
    return db.query(company_db.Company.company_name).all()
