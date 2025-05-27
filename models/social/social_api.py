from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social import social_db  # استورد الملف الجديد

router = APIRouter(prefix="/social", tags=["Social Media"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/analytics")
def get_social_analytics(db: Session = Depends(get_db)):
    try:
        return social_db.get_social_analytics(db)
    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
