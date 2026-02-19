# app/controllers/agent_controller.py

from app.utils.timer import get_time, calculate_time
from app.services.result_generator import generate_results_json
from app.db.database import SessionLocal
from app.db.models import Run, Fix


# -------------------------
# DUMMY FUNCTIONS (same)
# -------------------------
def clone_repo(repo_url):
    print(f"[INFO] Cloning repository: {repo_url}")


def create_branch(team, leader):
    return f"{team}_{leader}_AI_Fix".upper().replace(" ", "_")


def run_tests():
    return "dummy error log"


def check_ci_status():
    return "PASSED"


def run_agent_logic(logs):
    return [
        {
            "file": "src/utils.py",
            "bug_type": "LINTING",
            "line": 15,
            "status": "Fixed"
        }
    ]


# -------------------------
# MAIN CONTROLLER
# -------------------------

async def run_agent_controller(payload):
    start = get_time()

    db = SessionLocal()   # ✅ DB SESSION START

    try:
        repo_url = payload["repo_url"]
        team = payload["team_name"]
        leader = payload["leader_name"]

        print("\n========== AGENT START ==========")

        # STEP 1
        clone_repo(repo_url)

        # STEP 2
        branch = create_branch(team, leader)

        total_fixes = []
        status = "FAILED"

        # STEP 3 LOOP
        for iteration in range(5):
            logs = run_tests()
            errors = run_agent_logic(logs)

            if not errors:
                status = "PASSED"
                break

            total_fixes.extend(errors)
            check_ci_status()

        end = get_time()
        time_taken = calculate_time(start, end)

        # -------------------------
        # ✅ SAVE RUN TO DATABASE
        # -------------------------
        new_run = Run(
            repo_url=repo_url,
            branch=branch,
            status=status,
            iterations=iteration + 1,
            time_taken=time_taken
        )

        db.add(new_run)
        db.commit()
        db.refresh(new_run)

        print(f"[DB] Run saved with ID: {new_run.id}")

        # -------------------------
        # ✅ SAVE FIXES
        # -------------------------
        for fix in total_fixes:
            new_fix = Fix(
                run_id=new_run.id,
                file=fix["file"],
                bug_type=fix["bug_type"],
                line=fix["line"],
                status=fix["status"]
            )
            db.add(new_fix)

        db.commit()
        print(f"[DB] {len(total_fixes)} fixes saved")

        # -------------------------
        # GENERATE RESULT JSON
        # -------------------------
        result = generate_results_json(
            repo_url,
            branch,
            total_fixes,
            status,
            iteration + 1,
            time_taken
        )

        print("========== AGENT END ==========\n")

        return result

    finally:
        db.close()   # ✅ ALWAYS CLOSE SESSION
