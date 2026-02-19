# app/main.py

from fastapi import FastAPI
from app.routes.agent_routes import router
from app.db.database import engine
from app.db.models import Base

app = FastAPI()

# create tables
Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Backend Running 🚀"}
