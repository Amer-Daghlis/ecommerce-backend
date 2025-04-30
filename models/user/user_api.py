import requests  # Add this import for making HTTP requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from . import user_schema, user_db
from .security import verify_password, hash_password
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import Request
from pydantic import BaseModel


router = APIRouter(prefix="/users", tags=["Users"])

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  POST: Sign up user (register)✅
@router.post("/signup", response_model=user_schema.UserOut)
def signup_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_db.create_user(db, user)

#  POST: Sign in user (validate email & password)✅
@router.post("/signin")
def signin_user(data: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_db.get_user_by_email(db, data.user_email)
    if not db_user or not verify_password(data.user_password, db_user.user_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"IsUserDefined": True, "user_id": db_user.user_id}

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
    data = await request.json()
    access_token = data.get("accessToken")  # Token from frontend

    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")

    print("Received access token:", access_token)

    try:
        # Verify the Facebook token
        app_id = ""  # Replace with your Facebook app ID
        app_secret = ""  # Replace with your Facebook app secret
        url = f"https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email"
        
        # Make a request to Facebook Graph API
        response = requests.get(url)
        fb_data = response.json()
        print("Facebook API response:", fb_data)

        if "error" in fb_data:
            raise HTTPException(status_code=400, detail="Facebook login failed")

        # Extract user info from Facebook response
        email = fb_data.get("email")
        name = fb_data.get("name")

        # Handle user login/signup from Facebook
        user = user_db.get_or_create_facebook_user(db, email, name)
        
        return {"message": "Login successful", "user_id": user.user_id, "email": user.user_email}

    except Exception as e:
        print("Error during Facebook login:", str(e))
        raise HTTPException(status_code=400, detail=f"Facebook login failed: {str(e)}")

@router.post("/google-login")
async def google_login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    print("Received JSON from frontend:", data)  # ✅ Add this

    token = data.get("token")  # ✅ Make sure this matches frontend key

    if not token:
        raise HTTPException(status_code=400, detail="No token received")

    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
        email = idinfo["email"]
        name = idinfo.get("name", "")

        user = user_db.get_or_create_google_user(db, email, name)

        return {"message": "Login successful", "user_id": user.user_id, "email": user.user_email}

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
