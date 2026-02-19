# app/controllers/agent_controller.py

from app.utils.timer import get_time, calculate_time
from app.services.result_generator import generate_results_json

# these will come from your teammates
# TEMP dummy functions for now

def clone_repo(repo_url):
    print(f"Cloning {repo_url}")

def create_branch(team, leader):
    return f"{team}_{leader}_AI_Fix".upper().replace(" ", "_")

def run_tests():
    return "dummy error log"

def check_ci_status():
    return "PASSED"

def run_agent_logic(logs):
    # dummy fix output (replace with Member 1 logic)
    return [
        {
            "file": "src/utils.py",
            "bug_type": "LINTING",
            "line": 15,
            "status": "Fixed"
        }
    ]


async def run_agent_controller(payload):
    start = get_time()

    repo_url = payload["repo_url"]
    team = payload["team_name"]
    leader = payload["leader_name"]

    # STEP 1: Clone
    clone_repo(repo_url)

    # STEP 2: Branch
    branch = create_branch(team, leader)

    total_fixes = []
    status = "FAILED"

    # STEP 3: Retry loop
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

    # STEP 4: Generate results
    result = generate_results_json(
        repo_url,
        branch,
        total_fixes,
        status,
        iteration + 1,
        time_taken
    )

    return result
