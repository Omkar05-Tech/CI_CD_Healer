# app/routes/agent_routes.py

from fastapi import APIRouter
from app.controllers.agent_controller import run_agent_controller

router = APIRouter()

@router.post("/run-agent")
async def run_agent(payload: dict):
    return await run_agent_controller(payload)
