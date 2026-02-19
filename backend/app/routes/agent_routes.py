# # app/routes/agent_routes.py

# from fastapi import APIRouter, HTTPException
# from app.controllers.agent_controller import run_agent_controller
# from app.db.schemas import RunRequest

# router = APIRouter()

# @router.post("/run-agent")
# async def run_agent(payload: RunRequest):
#     try:
#         result = await run_agent_controller(payload.model_dump())
#         return {
#             "success": True,
#             "data": result
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas import RunRequest
from app.controllers.agent_controller import (
    handle_scan_logic, 
    handle_fix_logic, 
    get_fix_progress_logic
)

router = APIRouter(tags=["Healer Agent"])

@router.post("/scan-repo")
async def scan_repo_endpoint(payload: RunRequest):
    """Step 1: HTTP layer for scanning."""
    result = await handle_scan_logic(payload)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

@router.post("/fix-all")
async def fix_all_endpoint(team_name: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Step 2: HTTP layer for triggering background healing."""
    result = await handle_fix_logic(team_name, background_tasks, db)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result

@router.get("/fix-progress/{run_id}")
async def fix_progress_endpoint(run_id: int, db: Session = Depends(get_db)):
    """Step 3: HTTP layer for progress tracking."""
    result = await get_fix_progress_logic(run_id, db)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Run not found")
    return result