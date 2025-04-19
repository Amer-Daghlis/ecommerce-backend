from fastapi import FastAPI
from models.user import user_api
from models.product import product_api
from models.cart import cart_api
from models.categories import category_api
from models.companies import company_api
from models.wishlist import wishlist_api
from fastapi.middleware.cors import CORSMiddleware


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
