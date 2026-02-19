# from .analyzer_agent import AnalyzerAgent
# from .debugger_agent import DebuggerAgent
# from .fixer_agent import FixerAgent

# class AgentOrchestrator:
#     def __init__(self, mistral_api_key):
#         self.analyzer = AnalyzerAgent()
#         self.debugger = DebuggerAgent()
#         # Connects the Codestral service to the Fixer Agent
#         self.fixer = FixerAgent(mistral_api_key) 

#     async def run_iteration(self, repo_path, logs):
#         # 1. Analyzer Agent: Parse logs from Member 3 [cite: 13-15]
#         error_data = self.analyzer.process_logs(logs)
#         if not error_data:
#             return None # Tests passed
        
#         # 2. Fixer Agent: Call Codestral and rewrite file [cite: 15-16]
#         fix_info = await self.fixer.execute_fix(repo_path, error_data)
        
#         # 3. Debugger Agent: Create the Dashboard string for the Judges [cite: 63]
#         # Required format: "TYPE error in file line X -> Fix: summary"
#         summary = f"Codestral applied {error_data['bug_type'].lower()} patch"
#         fix_info["dashboard_output"] = self.debugger.get_dashboard_output(error_data, summary)
        
#         # Add metadata for results.json
#         fix_info.update(error_data)
#         return fix_info


import time
from datetime import datetime
from app.services.git_services import generate_results_json

async def run_full_agent(
    self,
    repo_path,
    logs_generator,   # function that gives logs each iteration
    repo_url,
    team_name,
    leader_name,
    branch_name,
    github_token,
    max_retries=5
):
    start_time = datetime.utcnow().isoformat()
    start = time.time()

    commit_counter = {"count": 0}
    iterations = 0
    all_fixes = []
    ci_status = "FAILED"

    for i in range(max_retries):
        iterations += 1

        # 🔁 Get fresh logs every iteration
        logs = logs_generator()

        # Use existing pipeline
        fix_info = await self.run_iteration(repo_path, logs)

        # ✅ No errors → CI PASSED
        if not fix_info:
            ci_status = "PASSED"
            break

        # 🔥 COMMIT + PUSH HERE (IMPORTANT)
        from app.services.git_services import commit_and_push

        result = commit_and_push(
            repo_path=repo_path,
            branch_name=branch_name,
            commit_message=fix_info["commit_msg"],
            github_token=github_token,
            repo_url=repo_url
        )

        if result["success"]:
            commit_counter["count"] += 1
            fix_info["status"] = "Fixed"
        else:
            fix_info["status"] = "Failed"

        all_fixes.append(fix_info)

    end = time.time()
    time_taken = end - start

    # 📊 Generate results.json (MANDATORY)
    generate_results_json(
        repo_url=repo_url,
        branch_name=branch_name,
        team_name=team_name,
        leader_name=leader_name,
        fixes=all_fixes,
        ci_status=ci_status,
        start_time=start_time,
        time_taken=time_taken,
        iterations=iterations,
        commit_count=commit_counter["count"]
    )

    return {
        "status": ci_status,
        "iterations": iterations,
        "commits": commit_counter["count"],
        "branch": branch_name
    }
