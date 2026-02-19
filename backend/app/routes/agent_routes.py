# app/routes/agent_routes.py

from fastapi import APIRouter, HTTPException
from app.controllers.agent_controller import run_agent_controller
from app.db.schemas import RunRequest

router = APIRouter()

@router.post("/run-agent")
async def run_agent(payload: RunRequest):
    try:
        result = await run_agent_controller(payload.dict())
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
