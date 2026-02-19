# app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)  # 👈 echo shows SQL logs
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# ✅ TEST CONNECTION
try:
    with engine.connect() as conn:
        print("✅ DATABASE CONNECTED SUCCESSFULLY")
except Exception as e:
    print("❌ DATABASE CONNECTION FAILED:", e)

def get_db():
    """
    FastAPI dependency to provide a database session per request.
    Automatically closes the session after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
