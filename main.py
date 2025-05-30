from fastapi import FastAPI
from models.user import user_api
from models.product import product_api
from models.cart import cart_api
from models.categories import category_api
from models.companies import company_api
from models.wishlist import wishlist_api
from models.order import order_api  
from fastapi.middleware.cors import CORSMiddleware
from models.Payment import pay_api   
from models.social import social_api
from models.order import TrackOrder_api
from models.driver import driver_api
from models.categories.sub_category_db import SubCategory
from models.orderInfo import order_info_api
from models.social.post import post_api
from models.social.comment import comment_api
from models.social.comment_reply import comment_reply_api
from models.social.report import reported_api


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔥 This enables GET/POST /users/ endpoints
app.include_router(user_api.router)
app.include_router(product_api.router)
app.include_router(cart_api.router)
app.include_router(category_api.router)
app.include_router(company_api.router)
app.include_router(wishlist_api.router)
app.include_router(order_api.router)
app.include_router(pay_api.router)
app.include_router(social_api.router)
app.include_router(TrackOrder_api.router)
app.include_router(driver_api.router)
app.include_router(order_info_api.router)
app.include_router(post_api.router)
app.include_router(comment_api.router)
app.include_router(comment_reply_api.router)
app.include_router(reported_api.router)




@app.get("/")
def root():
    return {"message": "Welcome to the backend API!"}
