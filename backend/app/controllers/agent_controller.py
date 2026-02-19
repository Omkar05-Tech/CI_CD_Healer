# import os
# from app.utils.timer import get_time, calculate_time #
# from app.services.result_generator import generate_results_json #
# from app.db.database import SessionLocal #
# from app.db.models import Run, Fix #

# # Import real services - ensure these paths match your file structure
# from app.services.git_services import clone_repo, create_branch #
# from app.services.test_runner import run_tests #
# from app.services.fixer_service import FixerService #
# from app.services.repo_scanner import scan_repo

# async def run_agent_controller(payload: dict):
#     start = get_time() #
#     db = SessionLocal() #
    
#     # Initialize your Fixer with the real key from .env
#     api_key = os.environ.get("MISTRAL_API_KEY") #
#     fixer = FixerService(api_key=api_key) #

#     try:
#         # Extracting real data from the updated RunRequest schema
#         repo_url = payload["repo_url"] #
#         team = payload["team_name"] #
#         leader = payload["leader_name"] #
#         github_token = payload.get("github_token") #

#         print("\n========== REAL AGENT START ==========")

#         # STEP 1: Real Clone - Returns local file system path
#         local_repo_path = clone_repo(repo_url)

#         # STEP 2: Real Branching - Enforces hackathon naming specs
#         branch = create_branch(local_repo_path, team, leader)

#         total_fixes = []
#         status = "FAILED"
        
#         # STEP 3: Real Iterative Loop
#         for iteration in range(5):
#             # Update the count so it saves correctly in DB
#             iteration_count = iteration + 1 
            
#             # Use the scanner to find real source code bugs
#             scan_report = scan_repo(local_repo_path, repo_url)
            
#             if scan_report["total_errors"] == 0:
#                 status = "PASSED"
#                 break
                
#             # Track files fixed in THIS iteration to avoid infinite loops
#             files_fixed_this_round = set() 

#             for failure in scan_report["errors"]:
#                 if failure['file'] in files_fixed_this_round:
#                     continue # Skip if we already touched this file in this loop

#                 await fixer.apply_and_push_fix(...)
#                 files_fixed_this_round.add(failure['file'])

#                 push_result = await fixer.apply_and_push_fix(
#                     repo_path=local_repo_path,
#                     failure=failure,
#                     branch_name=branch,
#                     github_token=github_token,
#                     repo_url=repo_url
#                 )
                
#                 if push_result.get("success"):
#                     # Mark as fixed so it saves correctly to DB
#                     failure["status"] = "Fixed" 
#                     total_fixes.append(failure)

#         # FINAL CHECK: Run one last scan to confirm if everything is truly healed
#         final_check = scan_repo(local_repo_path, repo_url)
#         if final_check["total_errors"] == 0:
#             status = "PASSED"

#         # STEP 4: Calculate time correctly within the try block to avoid scope errors
#         end = get_time() #
#         time_taken = calculate_time(start, end) #

#         # -------------------------
#         # ✅ SAVE RUN TO DATABASE
#         # -------------------------
#         new_run = Run(
#             repo_url=repo_url,
#             branch=branch,
#             status=status,
#             iterations=iteration_count,
#             time_taken=time_taken # Variable is now safely defined
#         )

#         db.add(new_run)
#         db.commit()
#         db.refresh(new_run)

#         # -------------------------
#         # ✅ SAVE REAL FIXES
#         # -------------------------
#         for fix in total_fixes:
#             new_fix = Fix(
#                 run_id=new_run.id,
#                 file=fix["file"],
#                 bug_type=fix["bug_type"], #
#                 line=fix["line"], #
#                 status=fix.get("status", "Fixed")
#             )
#             db.add(new_fix)

#         db.commit()

#         # -------------------------
#         # GENERATE RESULT JSON
#         # -------------------------
#         result = generate_results_json(
#             repo_url,
#             branch,
#             total_fixes,
#             status,
#             iteration_count,
#             time_taken
#         ) #

#         print("========== REAL AGENT END ==========\n")
#         return result

#     finally:
#         db.close() #

import os
from sqlalchemy.orm import Session
from app.db.models import Run, Fix
from app.services.git_services import clone_repo, create_branch
from app.services.repo_scanner import scan_repo
from app.services.fixer_service import FixerService

# Shared memory for the hackathon (use Redis for production)
SCAN_REPORTS = {}

async def handle_scan_logic(payload):
    try:
        local_path = clone_repo(payload.repo_url)
        report = scan_repo(local_path, payload.repo_url)
        
        # Cache report for the fix step
        SCAN_REPORTS[payload.team_name] = {
            "local_path": local_path,
            "report": report,
            "payload": payload.model_dump()
        }
        # Return the summary AND the detailed error list
        return {
            "success": True, 
            "total_errors": report["total_errors"], 
            "summary": report["summary"],
            "errors": report["errors"]  # 👈 Added this
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def handle_fix_logic(team_name: str, background_tasks, db):
    # 1. Validation: Ensure scan was performed in this session
    if team_name not in SCAN_REPORTS:
        return {
            "success": False, 
            "error": f"No scan report found for '{team_name}'. Please run /scan-repo first."
        }

    data = SCAN_REPORTS[team_name]
    
    try:
        # 2. Create the DB entry for tracking
        # We add user_id=1 and time_taken=0.0 to satisfy NOT NULL constraints
        new_run = Run(
            repo_url=data["payload"]["repo_url"],
            branch="PENDING",
            status="IN_PROGRESS",
            iterations=1,
            time_taken=0.0, # Initialize to avoid null errors
            user_id=1       # satisfy (psycopg2.errors.NotNullViolation)
        )
        
        db.add(new_run)
        db.commit()
        db.refresh(new_run)

        # 3. Hand off to background worker
        # Note: We pass the data dictionary which contains the local_path and report
        background_tasks.add_task(process_healing_task, new_run.id, data, db)
        
        return {
            "success": True, 
            "run_id": new_run.id,
            "message": f"Healing process started for team {team_name}"
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Database error: {str(e)}"}

async def get_fix_progress_logic(run_id, db):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run: return {"success": False}

    fixes = db.query(Fix).filter(Fix.run_id == run_id).all()
    return {
        "success": True,
        "status": run.status,
        "branch": run.branch,
        "fixed_count": len([f for f in fixes if f.status == "Fixed"]),
        "details": fixes
    }

async def process_healing_task(run_id, data, db):
    """The Sequential Worker."""
    fixer = FixerService(api_key=os.environ.get("MISTRAL_API_KEY"))
    local_path = data["local_path"]
    payload = data["payload"]
    report = data["report"]

    # Deduplicate: one fix per file to prevent push race conditions
    unique_failures = {err['file']: err for err in report['errors']}.values()
    
    branch = create_branch(local_path, payload["team_name"], payload["leader_name"])
    
    # Update Run with branch name
    run = db.query(Run).filter(Run.id == run_id).first()
    run.branch = branch
    db.commit()

    for failure in unique_failures:
        push_result = await fixer.apply_and_push_fix(
            repo_path=local_path,
            failure=failure,
            branch_name=branch,
            github_token=payload["github_token"],
            repo_url=payload["repo_url"]
        )

        new_fix = Fix(
            run_id=run_id,
            file=failure["file"],
            bug_type=failure["bug_type"],
            line=failure["line"],
            status="Fixed" if push_result["success"] else "Failed"
        )
        db.add(new_fix)
        db.commit()

    # Final Scan to verify
    final_report = scan_repo(local_path, payload["repo_url"])
    run.status = "PASSED" if final_report["total_errors"] == 0 else "FAILED"
    db.commit()