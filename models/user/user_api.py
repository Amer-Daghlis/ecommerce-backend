import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from . import user_schema, user_db
from .security import verify_password, hash_password, send_verification_email, generate_verification_code
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import Request
from pydantic import BaseModel
from datetime import datetime, timedelta 
from .user_db import VerificationCode
import os
from ..cart.cart_db import get_or_create_cart


# Import necessary modules
router = APIRouter(prefix="/users", tags=["Users"])

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST: Check email in database (for signup)✅
@router.post("/check-email")
def check_email(data: user_schema.CheckUserEmailDefine, db: Session = Depends(get_db)):
    db_user = user_db.get_user_by_email(db, data.user_email)
    if db_user:
        return {"IsUserDefined": True}
    return {"IsUserDefined": False}
#  POST: Verify email (send verification code)✅
@router.post("/verify-email")
def send_verification_code(data: user_schema.UserVerify, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta

    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=1)

    try:
        existing = db.query(VerificationCode).filter_by(email=data.user_email).first()
        if existing:
            existing.code = code
            existing.expires_at = expires_at
        else:
            new_entry = VerificationCode(
                email=data.user_email,
                code=code,
                expires_at=expires_at
            )
            db.add(new_entry)

        db.commit()

        # Comment out this temporarily if debugging
        send_verification_email(data.user_email, code)

        return {"message": "Verification code sent"}

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send verification code: {e}")

@router.post("/checkCode")
def verify_code(data: user_schema.CodeVerification, db: Session = Depends(get_db)):
    entry = db.query(VerificationCode).filter_by(email=data.email).first()
    print("Received email:", data.email)
    print("Received code:", data.code)
    print("Found in DB:", entry.code if entry else "No entry")
    if not entry or entry.code != data.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    if datetime.utcnow() > entry.expires_at:
        raise HTTPException(status_code=400, detail="Verification code expired")
    
    return {"message": "Email verified successfully"}



#  POST: Sign up user (register)✅
@router.post("/signup")  # ← no response_model
def signup_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    new_user = user_db.create_user(db, user)
    return {"user_id": new_user.user_id}



#  POST: Sign in user (validate email & password)✅
@router.post("/signin")
def signin_user(data: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_db.get_user_by_email(db, data.user_email)
    if not db_user or not verify_password(data.user_password, db_user.user_password):
        return {"IsUserDefined": False, "user_id": -1}
    return {"IsUserDefined": True, "user_id": db_user.user_id, "user_status": db_user.user_status}

#  GET: Get user by ID✅
@router.get("/{user_id}", response_model=user_schema.UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = user_db.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#  GET: Get user by name 📍
@router.get("/name/{username}", response_model=list[user_schema.UserOut])
def get_users_by_name(username: str, db: Session = Depends(get_db)):
    return user_db.get_users_by_name(db, username)

#  GET: Get all users
@router.get("/", response_model=list[user_schema.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return user_db.get_all_users(db)


@router.post("/facebook-login")
async def facebook_login(request: Request, db: Session = Depends(get_db)):
    FACEBOOK_APP_ID=717835217478182
    FACEBOOK_APP_SECRET="4b5c1c638f0dcd8eaf898caea9bf2f0b"


    data = await request.json()
    access_token = data.get("accessToken")

    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")

    try:
        # Validate token (optional but good)
        debug_url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={app_id}|{app_secret}"
        debug_resp = requests.get(debug_url).json()
        if "error" in debug_resp.get("data", {}):
            raise HTTPException(status_code=400, detail="Invalid Facebook token")

        # Fetch user info
        info_url = f"https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email"
        info_resp = requests.get(info_url).json()

        if "error" in info_resp:
            raise HTTPException(status_code=400, detail="Facebook login failed")

        email = info_resp.get("email")
        name = info_resp.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Facebook")

        user = user_db.get_or_create_facebook_user(db, email, name, access_token)
        return {"message": "Login successful", "user_id": user.user_id}

    except Exception as e:
        print("Error during Facebook login:", str(e))
        raise HTTPException(status_code=400, detail=f"Facebook login failed: {str(e)}")


@router.post("/google-login")
async def google_login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    print("Received JSON from frontend:", data)

    token = data.get("token")  # ✅ Make sure this matches frontend key

    if not token:
        raise HTTPException(status_code=400, detail="No token received")

    try:
        client_id = "631245239192-8cek364mrcs3477aet7poiv7tj0kn39c.apps.googleusercontent.com"
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        email = idinfo["email"]
        name = idinfo.get("name", "")

        user = user_db.get_or_create_google_user(db, email, name, token)

        return {"message": "Login successful", "user_id": user.user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google token verification failed: {str(e)}")

# GET: Get signup date by user_id
@router.get("/signup-date/{user_id}", response_model=user_schema.UserSignupDate)
def get_user_signup_date(user_id: int, db: Session = Depends(get_db)):
    signup_date = user_db.get_user_signup_date(db, user_id)
    if signup_date is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "signup_date": signup_date
    }



# GET: Get address by user_id
@router.get("/address/{user_id}", response_model=user_schema.UserAddress)
def get_user_address(user_id: int, db: Session = Depends(get_db)):
    address = user_db.get_user_address(db, user_id)
    if address is None:
        raise HTTPException(status_code=404, detail="User or address not found")
    return {"user_id": user_id, "address": address}


# GET: User contact info (name, email, phone, address)
@router.get("/contact/{user_id}", response_model=user_schema.UserContactInfo)
def get_user_contact_info(user_id: int, db: Session = Depends(get_db)):
    user = user_db.get_user_contact_info(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#************************************** Admin Section *****************************************#

# GET: Get all users (Admin only)
@router.get("/admin/users", response_model=list[user_schema.AdminUserOut])
def get_all_admin_user_data(db: Session = Depends(get_db)):
    return user_db.get_admin_users(db)

#
class UserStatusUpdate(BaseModel):
    status: int  # 0 or 1

@router.post("/set-status/{user_id}")
def post_set_user_status(user_id: int, data: UserStatusUpdate, db: Session = Depends(get_db)):
    if data.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="Status must be 0 or 1")
    
    user = user_db.set_user_status(db, user_id, data.status)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": f"User {user_id} status updated",
        "status": 1 if user.user_status else 0
    }

@router.get("/total-users/month", response_model=list[user_schema.MonthlyUserJoin])
def get_monthly_and_previous_revenue(db: Session = Depends(get_db)):
    from datetime import datetime
    now = datetime.now()

    # Current month
    current_month = now.month
    current_year = now.year

    # Previous month logic
    if now.month == 1:
        previous_month = 12
        previous_year = now.year - 1
    else:
        previous_month = now.month - 1
        previous_year = now.year

    current_revenue = user_db.get_customer_join_for_month(db, current_year, current_month)
    previous_revenue = user_db.get_customer_join_for_month(db, previous_year, previous_month)

    return  [
    {"month": current_month, "year": current_year, "total_users": current_revenue},
    {"month": previous_month, "year": previous_year, "total_users": previous_revenue}
]
