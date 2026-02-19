# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.db import models
from app.db.database import engine
from app.db.models import Base
from dotenv import load_dotenv
import os
load_dotenv()

# ✅ Import all routers
from app.routes.agent_routes import router as agent_router
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="CI/CD Healing Agent API 🚀"
)

# models.Base.metadata.create_all(bind=engine)
# ---------------------------
# 🌐 CORS Middleware (IMPORTANT for frontend)
# ---------------------------
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY") # ✅ MUST MATCH YOUR .env
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # React (Vite)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# 📦 Include Routers
# ---------------------------
app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])

# ---------------------------
# 🏠 Root Endpoint
# ---------------------------
@app.get("/")
def home():
    return {
        "message": "🚀 CI/CD Healing Agent Backend Running",
        "status": "OK"
    }

