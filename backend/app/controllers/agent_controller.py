# import os
# from sqlalchemy.orm import Session
# from app.db.models import Run, Fix
# from app.services.git_services import clone_repo, create_branch
# from app.services.repo_scanner import scan_repo
# from app.services.fixer_service import FixerService

# # Shared memory for the hackathon (use Redis for production)
# SCAN_REPORTS = {}

# async def handle_scan_logic(payload):
#     try:
#         # 🚨 FIX: Use dot notation for Pydantic objects
#         local_path = clone_repo(payload.repo_url)
        
#         # Run the scanner
#         report = scan_repo(local_path, payload.repo_url)
        
#         # Store metadata using model_dump() for the dictionary
#         SCAN_REPORTS[payload.team_name] = {
#             "local_path": local_path,
#             "report": report,
#             "payload": payload.model_dump() # Converts object to dict for storage
#         }

#         return {
#             "success": True, 
#             "total_errors": report["total_errors"], 
#             "summary": report["summary"],
#             "errors": report["errors"]
#         }
#     except Exception as e:
#         print(f"[SCAN ERROR] {str(e)}")
#         return {"success": False, "error": str(e)}

# async def handle_fix_logic(team_name: str, background_tasks, db):
#     # 1. Validation: Ensure scan was performed in this session
#     if team_name not in SCAN_REPORTS:
#         return {
#             "success": False, 
#             "error": f"No scan report found for '{team_name}'. Please run /scan-repo first."
#         }

#     data = SCAN_REPORTS[team_name]
    
#     try:
#         # 2. Create the DB entry for tracking
#         # We add user_id=1 and time_taken=0.0 to satisfy NOT NULL constraints
#         new_run = Run(
#             repo_url=data["payload"]["repo_url"],
#             branch="PENDING",
#             status="IN_PROGRESS",
#             iterations=1,
#             time_taken=0.0, # Initialize to avoid null errors
#             user_id=1       # satisfy (psycopg2.errors.NotNullViolation)
#         )
        
#         db.add(new_run)
#         db.commit()
#         db.refresh(new_run)

#         # 3. Hand off to background worker
#         # Note: We pass the data dictionary which contains the local_path and report
#         background_tasks.add_task(process_healing_task, new_run.id, data, db)
        
#         return {
#             "success": True, 
#             "run_id": new_run.id,
#             "message": f"Healing process started for team {team_name}"
#         }

#     except Exception as e:
#         db.rollback()
#         return {"success": False, "error": f"Database error: {str(e)}"}

# async def get_fix_progress_logic(run_id, db):
#     run = db.query(Run).filter(Run.id == run_id).first()
#     if not run: return {"success": False}

#     fixes = db.query(Fix).filter(Fix.run_id == run_id).all()
#     return {
#         "success": True,
#         "status": run.status,
#         "branch": run.branch,
#         "fixed_count": len([f for f in fixes if f.status == "Fixed"]),
#         "details": fixes
#     }

# async def process_healing_task(run_id, data, db):
#     """The Sequential Worker."""
#     fixer = FixerService(api_key=os.environ.get("MISTRAL_API_KEY"))
#     local_path = data["local_path"]
#     payload = data["payload"]
#     report = data["report"]

#     # Deduplicate: one fix per file to prevent push race conditions
#     unique_failures = {err['file']: err for err in report['errors']}.values()
    
#     branch = create_branch(local_path, payload["team_name"], payload["leader_name"])
    
#     # Update Run with branch name
#     run = db.query(Run).filter(Run.id == run_id).first()
#     run.branch = branch
#     db.commit()

#     for failure in unique_failures:
#         push_result = await fixer.apply_and_push_fix(
#             repo_path=local_path,
#             failure=failure,
#             branch_name=branch,
#             github_token=payload["github_token"],
#             repo_url=payload["repo_url"]
#         )

#         new_fix = Fix(
#             run_id=run_id,
#             file=failure["file"],
#             bug_type=failure["bug_type"],
#             line=failure["line"],
#             status="Fixed" if push_result["success"] else "Failed"
#         )
#         db.add(new_fix)
#         db.commit()

#     # Final Scan to verify
#     final_report = scan_repo(local_path, payload["repo_url"])
#     run.status = "PASSED" if final_report["total_errors"] == 0 else "FAILED"
#     db.commit()

import os
import json
from sqlalchemy.orm import Session
from app.db.models import Run, Fix
from app.services.git_services import clone_repo, create_branch, commit_and_push
from app.services.repo_scanner import scan_repo
from app.agents.agent_orchestrator import AgentOrchestrator

# Shared memory for the hackathon session
SCAN_REPORTS = {}

async def handle_scan_logic(payload):
    """
    Step 1 Logic: Fresh Clone and Scan.
    Utilizes the dot notation for the RunRequest Pydantic model.
    """
    try:
        # Fresh clone every time to ensure we have the latest code
        local_path = clone_repo(payload.repo_url)
        
        # Run static analysis
        report = scan_repo(local_path, payload.repo_url)
        
        # Cache for Step 2
        SCAN_REPORTS[payload.team_name] = {
            "local_path": local_path,
            "report": report,
            "payload": payload.model_dump()
        }

        return {
            "success": True, 
            "total_errors": report["total_errors"], 
            "summary": report["summary"],
            "errors": report["errors"]
        }
    except Exception as e:
        print(f"[SCAN ERROR] {str(e)}")
        return {"success": False, "error": str(e)}

async def handle_fix_logic(team_name, background_tasks, db):
    """
    Step 2 Logic: Background task initialization.
    Fixes the NotNullViolation by providing default values.
    """
    if team_name not in SCAN_REPORTS:
        return {"success": False, "error": f"No scan report found for {team_name}."}

    data = SCAN_REPORTS[team_name]
    
    # Create the DB entry with required fields to satisfy PostgreSQL constraints
    new_run = Run(
        repo_url=data["payload"]["repo_url"],
        branch="PENDING",
        status="IN_PROGRESS",
        iterations=1,
        time_taken=0.0,
        user_id=1  # Default ID to avoid NotNullViolation
    )
    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    # Trigger sequential multi-agent healing
    background_tasks.add_task(process_healing_task, new_run.id, data, db)
    
    return {"success": True, "run_id": new_run.id}

async def get_fix_progress_logic(run_id, db):
    """Step 3 Logic: Live database query for progress."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        return {"success": False}

    fixes = db.query(Fix).filter(Fix.run_id == run_id).all()
    return {
        "success": True,
        "status": run.status,
        "branch": run.branch,
        "fixed_count": len([f for f in fixes if f.status == "Fixed"]),
        "details": fixes
    }

async def process_healing_task(run_id, data, db):
    """
    The sequential Multi-Agent worker.
    Delegates to Analyzer, Debugger, and Fixer agents.
    """
    # Initialize the Orchestrator with your Mistral Key
    orchestrator = AgentOrchestrator(mistral_api_key=os.environ.get("MISTRAL_API_KEY"))
    
    local_path = data["local_path"]
    payload = data["payload"]
    report = data["report"]

    # Deduplicate: one fix per file to prevent push race conditions
    unique_failures = {err['file']: err for err in report['errors']}.values()
    
    # Initialize the specific AI branch
    branch = create_branch(local_path, payload["team_name"], payload["leader_name"])
    
    # Update Run record with the branch name
    run = db.query(Run).filter(Run.id == run_id).first()
    run.branch = branch
    db.commit()

    for failure in unique_failures:
        # --- MULTI-AGENT HANDOFF ---
        # 1. Debugger validates the bug_type
        # 2. Fixer generates code and commit message
        agent_result = await orchestrator.run_iteration(local_path, failure) #

        if agent_result:
            # Safe sequential push with 'pull before push' logic
            push_result = commit_and_push(
                repo_path=local_path,
                branch_name=branch,
                commit_message=agent_result.get("commit_msg", "Apply AI Fix"),
                github_token=payload["github_token"],
                repo_url=payload["repo_url"]
            )

            # Record result using Agent's validated metadata
            new_fix = Fix(
                run_id=run_id,
                file=failure["file"],
                bug_type=agent_result.get("bug_type", failure["bug_type"]),
                line=failure["line"],
                status="Fixed" if push_result["success"] else "Failed"
            )
            db.add(new_fix)
            db.commit()

    # Final Verification Scan
    final_report = scan_repo(local_path, payload["repo_url"])
    run.status = "PASSED" if final_report["total_errors"] == 0 else "FAILED"
    db.commit()