# app/services/result_generator.py
import json
import os

def generate_results_json(repo, branch, fixes, status, iterations, time_taken):
    result = {
        "repository": repo,
        "branch": branch,
        "status": status,
        "iterations": iterations,
        "time_taken": time_taken,
        "total_fixes": len(fixes),
        "fixes": fixes
    }

    os.makedirs("results", exist_ok=True)

    with open("results/results.json", "w") as f:
        json.dump(result, f, indent=4)

    return result
