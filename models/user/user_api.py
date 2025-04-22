from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from . import user_schema, user_db
from .security import verify_password
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import Request
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
