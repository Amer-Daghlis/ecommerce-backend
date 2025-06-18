from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.social.report import reported_post_model, reported_db
from models.social.report.reported_post_model import ReportPostIn, ReportPostOut
from models.social.report import reported_post_model
from models.social.report import reported_comment_model
from models.social.report.reported_comment_model import ReportCommentIn, ReportCommentOut
from models.social.report.reported_reply_comment_model import ReportReplyIn, ReportReplyOut


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


@router.post("/reply", response_model=ReportReplyOut)
def report_comment_reply(data: ReportReplyIn, db: Session = Depends(get_db)):
    try:
        report_date, reply_status = reported_db.report_reply(db, data.user_id, data.reply_id, data.note)
        return {
            "message": "Report submitted successfully",
            "report_date": report_date,
            "reply_status": reply_status
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
       # How to test this API:
       # {
       #  "user_id": 1,
       #  "reply_id": 1,
       #  "note": "WeWe."
       # }


@router.get("/random-reports")
def get_random_reports(db: Session = Depends(get_db)):
    try:
        data = reported_db.get_random_reported_items(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/all-reported")
def get_all_reported(db: Session = Depends(get_db)):
    try:
        data = reported_db.get_all_reported_data(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

from pydantic import BaseModel

class SetReportStatusIn(BaseModel):
    report_id: int
    report_type: str
    new_status: str

@router.put("/set-status")
def update_report_status(data: SetReportStatusIn, db: Session = Depends(get_db)):
    try:
        return reported_db.set_report_status(db, data.report_id, data.report_type, data.new_status)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
