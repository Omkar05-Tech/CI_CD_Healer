# app/db/models.py
# from sqlalchemy import Column, Integer, String, Float, ForeignKey
# from app.db.database import Base

# class Run(Base):
#     __tablename__ = "runs"

#     id = Column(Integer, primary_key=True, index=True)
#     repo_url = Column(String)
#     branch = Column(String)
#     status = Column(String)
#     iterations = Column(Integer)
#     time_taken = Column(Float)


# class Fix(Base):
#     __tablename__ = "fixes"

#     id = Column(Integer, primary_key=True, index=True)
#     run_id = Column(Integer, ForeignKey("runs.id"))
#     file = Column(String)
#     bug_type = Column(String)
#     line = Column(Integer)
#     status = Column(String)


from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


# -------------------------
# USER MODEL
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ Correctly links to Run
    runs = relationship("Run", back_populates="user")


# -------------------------
# RUN MODEL
# -------------------------
class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String)
    branch = Column(String)
    status = Column(String, default="running")
    iterations = Column(Integer, default=0)
    time_taken = Column(Float, default=0.0)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # ✅ Relationships
    user = relationship("User", back_populates="runs")
    # ✅ back_populates="run" matches the attribute name added to Fix below
    fixes = relationship("Fix", back_populates="run", cascade="all, delete", passive_deletes=True)


# -------------------------
# FIX MODEL
# -------------------------
class Fix(Base):
    __tablename__ = "fixes"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    file = Column(String)
    bug_type = Column(String)
    line = Column(Integer)
    status = Column(String)

    # ✅ FIXED: Added relationship to link back to the Run model
    # This resolves the Mapper error by providing the 'run' property
    run = relationship("Run", back_populates="fixes")
