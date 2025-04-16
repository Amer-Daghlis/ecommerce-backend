from fastapi import FastAPI
from models.user import user_api

app = FastAPI()

# 🔥 This enables GET/POST /users/ endpoints
app.include_router(user_api.router)
