# app/db/schemas.py
from pydantic import BaseModel

class RunRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str


class RunResponse(BaseModel):
    status: str
    iterations: int
    total_fixes: int
    time_taken: float
