# app/db/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.database import Base

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String)
    branch = Column(String)
    status = Column(String)
    iterations = Column(Integer)
    time_taken = Column(Float)


class Fix(Base):
    __tablename__ = "fixes"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    file = Column(String)
    bug_type = Column(String)
    line = Column(Integer)
    status = Column(String)
