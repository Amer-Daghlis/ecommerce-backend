from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social.report import reported_post_model, reported_db
from models.social.report.reported_post_model import ReportPostIn, ReportPostOut
from models.social.report import reported_post_model
from models.social.report import reported_comment_model


router = APIRouter(prefix="/report", tags=["Report"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/post", response_model=reported_post_model.ReportPostOut)
def report_post(data: reported_post_model.ReportPostIn, db: Session = Depends(get_db)):
    try:
        report_date, post_status = reported_db.report_post(db, data.user_id, data.post_id, data.note)
        return {
            "message": "Report submitted successfully",
            "report_date": report_date,
            "post_status": post_status
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/comment", response_model=reported_comment_model.ReportCommentOut)
def report_comment(data: reported_comment_model.ReportCommentIn, db: Session = Depends(get_db)):
    try:
        report_date, comment_status = reported_db.report_comment(db, data.user_id, data.comment_id, data.note)
        return {
            "message": "Report submitted successfully",
            "report_date": report_date,
            "comment_status": comment_status
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
