# # app/services/github_service.py 
# # Member 2 — System + DevOps + Execution 
# # Handles: repo cloning, branch creation, commit & push 
 
# import os 
# import re 
# import sys 
# import stat 
# import shutil 
# import logging 
# import tempfile 
# from git import Repo, GitCommandError 
 
# logger = logging.getLogger(__name__) 
 
# # Use OS-appropriate temp directory (fixes WinError 5 on Windows) 
# CLONE_BASE = os.path.join(tempfile.gettempdir(), "agent_repos") 
 
 
# def _force_remove(path: str): 
#     """ 
#     Force-delete a directory on any OS. 
#     On Windows, git sets files to read-only which causes WinError 5. 
#     This handler removes read-only flag before deleting. 
#     """ 
#     def handle_readonly(func, fpath, excinfo): 
#         try: 
#             os.chmod(fpath, stat.S_IWRITE) 
#             func(fpath) 
#         except Exception: 
#             pass 
#     if os.path.exists(path): 
#         shutil.rmtree(path, onerror=handle_readonly) 
 
 
# def _sanitize_for_branch(text: str) -> str: 
#     """ 
#     Convert any string to UPPERCASE_WITH_UNDERSCORES. 
#     Strips all special chars except underscores. 
#     Required by hackathon spec: TEAM_NAME_LEADER_NAME_AI_Fix 
#     """ 
#     text = text.upper().strip() 
#     text = re.sub(r'\s+', '_', text)           # spaces → underscores 
#     text = re.sub(r'[^A-Z0-9_]', '', text)     # strip special chars 
#     text = re.sub(r'_+', '_', text)            # collapse multiple underscores 
#     text = text.strip('_')                      # remove leading/trailing underscores 
#     return text 
 
 
# def clone_repo(repo_url: str) -> str: 
#     """ 
#     Clone the given GitHub repository to /tmp/agent_repos/<repo_name>. 
#     If already exists, deletes and re-clones for a clean state. 
 
#     Returns: 
#         str: Local path to the cloned repository. 
 
#     Raises: 
#         GitCommandError: If cloning fails (bad URL, auth issue, etc.) 
#     """ 
#     repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "") 
#     local_path = os.path.join(CLONE_BASE, repo_name) 
 
#     # Clean slate — force remove even if git locked files (Windows fix) 
#     _force_remove(local_path) 
 
#     os.makedirs(CLONE_BASE, exist_ok=True) 
 
#     logger.info(f"[CLONE] Cloning {repo_url} → {local_path}") 
#     Repo.clone_from(repo_url, local_path) 
#     logger.info(f"[CLONE] Done.") 
 
#     return local_path 
 
 
# def create_branch(repo_path: str, team_name: str, leader_name: str) -> str: 
#     """ 
#     Create a new branch from HEAD with the EXACT required format: 
#         TEAM_NAME_LEADER_NAME_AI_Fix  (all uppercase, underscores, no special chars) 
 
#     DISQUALIFICATION RISK: Wrong format → immediate DQ. 
#     This function enforces the format strictly. 
 
#     Returns: 
#         str: The created branch name. 
 
#     Raises: 
#         GitCommandError: If branch already exists or repo is invalid. 
#     """ 
#     team_sanitized = _sanitize_for_branch(team_name) 
#     leader_sanitized = _sanitize_for_branch(leader_name) 
 
#     # CRITICAL: Exact format as per hackathon spec 
#     branch_name = f"{team_sanitized}_{leader_sanitized}_AI_Fix" 
 
#     repo = Repo(repo_path) 
 
#     # Guard: never allow pushing to main/master 
#     current = repo.active_branch.name 
#     if current in ("main", "master"): 
#         repo.git.checkout('-b', branch_name) 
#         logger.info(f"[BRANCH] Created branch: {branch_name}") 
#     else: 
#         # Already on a non-main branch (shouldn't happen on fresh clone, but be safe) 
#         repo.git.checkout('-b', branch_name) 
#         logger.info(f"[BRANCH] Created branch: {branch_name}") 
 
#     return branch_name 
 
 
# def commit_and_push( 
#     repo_path: str, 
#     branch_name: str, 
#     commit_message: str, 
#     github_token: str, 
#     repo_url: str 
# ) -> dict: 
#     """ 
#     Stage all changes, commit with mandatory [AI-AGENT] prefix, and push to remote. 
 
#     DISQUALIFICATION RISKS HANDLED: 
#       1. Commits without [AI-AGENT] prefix → enforced here, impossible to bypass 
#       2. Pushing to main → guarded, only pushes to branch_name 
#       3. Wrong branch name → branch_name comes from create_branch(), already validated 
 
#     Args: 
#         repo_path:      Local path to cloned repo 
#         branch_name:    Branch to push to (must be from create_branch()) 
#         commit_message: Short description of the fix (NO prefix needed, added here) 
#         github_token:   GitHub Personal Access Token for auth 
#         repo_url:       Original HTTPS repo URL (token will be injected) 
 
#     Returns: 
#         dict with commit sha, branch, message, success flag 
#     """ 
#     repo = Repo(repo_path) 
 
#     # Safety guard: NEVER push to main/master 
#     if branch_name.lower() in ("main", "master"): 
#         raise ValueError( 
#             f"CRITICAL: Refusing to push to protected branch '{branch_name}'. " 
#             "Use create_branch() to get a valid AI_Fix branch." 
#         ) 
 
#     # Check if there's anything to commit 
#     if not repo.is_dirty(untracked_files=True): 
#         logger.info("[COMMIT] No changes to commit.") 
#         return { 
#             "success": False, 
#             "reason": "no_changes", 
#             "branch": branch_name 
#         } 
 
#     # Stage all changes (modified + new files) 
#     repo.git.add(A=True) 
 
#     # CRITICAL: [AI-AGENT] prefix is MANDATORY — disqualification if missing 
#     full_message = f"[AI-AGENT] {commit_message}" 
 
#     commit = repo.index.commit(full_message) 
#     logger.info(f"[COMMIT] {full_message} → sha: {commit.hexsha[:8]}") 
 
#     # Inject token into HTTPS URL for authentication 
#     # Transforms: https://github.com/user/repo 
#     #         to: https://<token>@github.com/user/repo 
#     clean_url = repo_url.replace("https://", "").replace("http://", "") 
#     auth_url = f"https://{github_token}@{clean_url}" 
 
#     try: 
#         origin = repo.remote(name='origin') 
#         origin.set_url(auth_url) 
 
#         # Push ONLY to the AI_Fix branch — never to main 
#         push_result = origin.push(refspec=f"refs/heads/{branch_name}:refs/heads/{branch_name}") 
 
#         logger.info(f"[PUSH] Pushed to remote branch: {branch_name}") 
 
#         return { 
#             "success": True, 
#             "branch": branch_name, 
#             "commit_sha": commit.hexsha, 
#             "commit_message": full_message, 
#             "push_summary": str(push_result[0].summary) if push_result else "ok" 
#         } 
 
#     except GitCommandError as e: 
#         logger.error(f"[PUSH] Failed: {e}") 
#         return { 
#             "success": False, 
#             "reason": str(e), 
#             "branch": branch_name, 
#             "commit_sha": commit.hexsha, 
#             "commit_message": full_message 
#         } 
#     finally: 
#         # Always clean up token from remote URL after use (security) 
#         try: 
#             origin.set_url(repo_url) 
#         except Exception: 
#             pass 
 
 
# def get_repo_info(repo_path: str) -> dict: 
#     """ 
#     Extract basic repo metadata for dashboard display. 
 
#     Returns: 
#         dict with current branch, commit count, remote URL 
#     """ 
#     repo = Repo(repo_path) 
#     return { 
#         "current_branch": repo.active_branch.name, 
#         "commit_count": len(list(repo.iter_commits())), 
#         "remote_url": repo.remotes.origin.url if repo.remotes else None, 
#         "is_dirty": repo.is_dirty(untracked_files=True) 
#     }

# app/services/github_service.py
# Member 2 — System + DevOps + Execution
# Handles: repo cloning, branch creation, commit & push, results.json

import os
import re
import sys
import stat
import json
import shutil
import logging
import tempfile
from datetime import datetime
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)

# Use OS-appropriate temp directory (fixes WinError 5 on Windows)
CLONE_BASE = os.path.join(tempfile.gettempdir(), "agent_repos")


def _force_remove(path: str):
    """
    Force-delete a directory on any OS.
    On Windows, git sets files to read-only which causes WinError 5.
    This handler removes read-only flag before deleting.
    """
    def handle_readonly(func, fpath, excinfo):
        try:
            os.chmod(fpath, stat.S_IWRITE)
            func(fpath)
        except Exception:
            pass
    if os.path.exists(path):
        shutil.rmtree(path, onerror=handle_readonly)


def _sanitize_for_branch(text: str) -> str:
    """
    Convert any string to UPPERCASE_WITH_UNDERSCORES.
    Strips all special chars except underscores.
    Required by hackathon spec: TEAM_NAME_LEADER_NAME_AI_Fix
    """
    text = text.upper().strip()
    text = re.sub(r'\s+', '_', text)           # spaces → underscores
    text = re.sub(r'[^A-Z0-9_]', '', text)     # strip special chars
    text = re.sub(r'_+', '_', text)            # collapse multiple underscores
    text = text.strip('_')                      # remove leading/trailing underscores
    return text


def clone_repo(repo_url: str) -> str:
    """
    Clone the given GitHub repository to temp/agent_repos/<repo_name>.
    If already exists, force-deletes and re-clones for a clean state.

    Returns:
        str: Local path to the cloned repository.
    """
    repo_name  = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    local_path = os.path.join(CLONE_BASE, repo_name)

    # Clean slate — force remove even if git locked files (Windows fix)
    _force_remove(local_path)

    os.makedirs(CLONE_BASE, exist_ok=True)

    logger.info(f"[CLONE] Cloning {repo_url} → {local_path}")
    Repo.clone_from(repo_url, local_path)
    logger.info(f"[CLONE] Done.")

    return local_path


def create_branch(repo_path: str, team_name: str, leader_name: str) -> str:
    """
    Create a new branch with EXACT required format:
        TEAM_NAME_LEADER_NAME_AI_Fix  (all uppercase, underscores only)

    DISQUALIFICATION RISK: Wrong format = immediate DQ.

    Returns:
        str: The created branch name.
    """
    team_sanitized   = _sanitize_for_branch(team_name)
    leader_sanitized = _sanitize_for_branch(leader_name)

    # CRITICAL: Exact format as per hackathon spec
    branch_name = f"{team_sanitized}_{leader_sanitized}_AI_Fix"

    repo = Repo(repo_path)
    repo.git.checkout('-b', branch_name)
    logger.info(f"[BRANCH] Created branch: {branch_name}")

    return branch_name


# def commit_and_push(
#     repo_path: str,
#     branch_name: str,
#     commit_message: str,
#     github_token: str,
#     repo_url: str
# ) -> dict:
#     """
#     Stage all changes, commit with mandatory [AI-AGENT] prefix, push directly
#     to remote branch — NO pull request, direct commit only.

#     DISQUALIFICATION RISKS HANDLED:
#       1. [AI-AGENT] prefix → enforced here, impossible to bypass
#       2. Push to main → guarded, only pushes to branch_name
#       3. Pull requests → NOT used, direct push via refspec
#       4. Token exposed → cleaned from remote URL after push

#     Returns:
#         dict with success, commit_sha, branch, commit_message
#     """
#     repo = Repo(repo_path)

#     # Safety guard: NEVER push to main/master — immediate DQ
#     if branch_name.lower() in ("main", "master"):
#         raise ValueError(
#             f"CRITICAL: Refusing to push to protected branch '{branch_name}'."
#         )

#     # Nothing to commit?
#     if not repo.is_dirty(untracked_files=True):
#         logger.info("[COMMIT] No changes to commit.")
#         return {"success": False, "reason": "no_changes", "branch": branch_name}

#     # Stage all changes
#     repo.git.add(A=True)

#     # CRITICAL: [AI-AGENT] prefix is MANDATORY — DQ if missing
#     full_message = f"[AI-AGENT] {commit_message}"
#     commit = repo.index.commit(full_message)
#     logger.info(f"[COMMIT] {full_message} → sha: {commit.hexsha[:8]}")

#     # Inject token into URL for auth (never stored permanently)
#     clean_url = repo_url.replace("https://", "").replace("http://", "").rstrip(".git")
#     auth_url  = f"https://{github_token}@{clean_url}"

#     try:
#         origin = repo.remote(name='origin')
#         origin.set_url(auth_url)

#         # DIRECT PUSH to branch — NO pull request created
#         # refspec format: local_branch:remote_branch
#         push_result = origin.push(
#             refspec=f"refs/heads/{branch_name}:refs/heads/{branch_name}"
#         )

#         logger.info(f"[PUSH] ✓ Pushed directly to branch: {branch_name}")

#         return {
#             "success":        True,
#             "branch":         branch_name,
#             "commit_sha":     commit.hexsha,
#             "commit_message": full_message,
#             "push_summary":   str(push_result[0].summary) if push_result else "ok"
#         }

#     except GitCommandError as e:
#         logger.error(f"[PUSH] ✗ Failed: {e}")
#         return {
#             "success":        False,
#             "reason":         str(e),
#             "branch":         branch_name,
#             "commit_sha":     commit.hexsha,
#             "commit_message": full_message
#         }
#     finally:
#         # Always clean token from remote URL (security)
#         try:
#             origin.set_url(f"https://github.com/{clean_url.split('github.com/')[-1]}")
#         except Exception:
#             pass

# app/services/git_services.py

def commit_and_push(repo_path, branch_name, commit_message, github_token, repo_url):
    repo = Repo(repo_path)
    repo.git.add(A=True)
    full_message = f"[AI-AGENT] {commit_message}"
    commit = repo.index.commit(full_message)

    clean_url = repo_url.replace("https://", "").replace("http://", "")
    auth_url = f"https://{github_token}@{clean_url}"

    try:
        origin = repo.remote(name='origin')
        origin.set_url(auth_url)

        # ─── PULL BEFORE PUSH (Crucial for sequential fixes) ───
        try:
            # Fetch to see if branch exists on remote
            origin.fetch()
            if f"origin/{branch_name}" in [ref.name for ref in origin.refs]:
                repo.git.pull('origin', branch_name)
                print(f"[GIT] Pulled latest from {branch_name}")
        except Exception as e:
            print(f"[GIT] No remote branch to pull yet or pull failed: {e}")

        # ─── THE PUSH ───
        push_info = origin.push(refspec=f"refs/heads/{branch_name}:refs/heads/{branch_name}")
        
        # 🚨 CHECK FOR PUSH ERRORS
        info = push_info[0]
        if info.flags & info.ERROR:
            error_msg = f"Push failed: {info.summary}"
            print(f"[GIT ERROR] {error_msg}")
            return {"success": False, "reason": error_msg}

        print(f"[GIT SUCCESS] Pushed {commit.hexsha[:7]} to {branch_name}")
        return {"success": True, "branch": branch_name, "sha": commit.hexsha}

    except Exception as e:
        print(f"[GIT CRITICAL ERROR] {str(e)}")
        return {"success": False, "reason": str(e)}
    finally:
        origin.set_url(repo_url)


def generate_results_json(
    repo_url: str,
    branch_name: str,
    team_name: str,
    leader_name: str,
    fixes: list,
    ci_status: str,
    start_time: str,
    time_taken: float,
    iterations: int,
    max_retries: int = 5
) -> dict:
    """
    Generate results.json — MANDATORY per hackathon spec.
    Judges check for this file at end of each run.

    Includes all fields required by the dashboard:
      - Run Summary Card
      - Score Breakdown Panel
      - Fixes Applied Table
      - CI/CD Status Timeline
    """
    total_fixes   = len(fixes)
    total_fixed   = len([f for f in fixes if f.get("status") == "Fixed"])
    total_failed  = len([f for f in fixes if f.get("status") != "Fixed"])

    # Score calculation per spec
    base_score         = 100
    speed_bonus        = 10 if time_taken < 300 else 0   # +10 if under 5 min
    efficiency_penalty = max(0, (total_fixed - 20) * 2)  # -2 per commit over 20
    final_score        = base_score + speed_bonus - efficiency_penalty

    results = {
        # Run Summary Card
        "repository":          repo_url,
        "branch":              branch_name,
        "team_name":           team_name,
        "leader_name":         leader_name,
        "start_time":          start_time,
        "end_time":            datetime.utcnow().isoformat(),
        "time_taken_seconds":  round(time_taken, 2),
        "total_failures_detected": total_fixes,
        "total_fixes_applied":     total_fixed,
        "ci_status":           ci_status,   # PASSED / FAILED

        # Score Breakdown Panel (required by dashboard spec)
        "score_breakdown": {
            "base_score":         base_score,
            "speed_bonus":        speed_bonus,
            "efficiency_penalty": efficiency_penalty,
            "final_score":        final_score,
            "commit_count":       total_fixed,
            "under_5_minutes":    time_taken < 300
        },

        # Fixes Applied Table (file, bug_type, line, commit_message, status)
        "fixes": [
            {
                "file":           f.get("file"),
                "bug_type":       f.get("bug_type"),
                "line_number":    f.get("line_number") or f.get("line", 0),
                "commit_message": f"[AI-AGENT] Fix {f.get('bug_type')} in {f.get('file')} line {f.get('line_number', 0)}",
                "status":         f.get("status", "Failed")
            }
            for f in fixes
        ],

        # CI/CD Timeline
        "ci_history": {
            "iterations_used": iterations,
            "max_retries":     max_retries,
            "final_status":    ci_status
        }
    }

    # Save to results/results.json — mandatory per spec
    os.makedirs("results", exist_ok=True)
    results_path = os.path.join("results", "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"[RESULTS] results.json saved → score: {final_score}")
    return results


def get_repo_info(repo_path: str) -> dict:
    """Extract basic repo metadata for dashboard display."""
    repo = Repo(repo_path)
    return {
        "current_branch": repo.active_branch.name,
        "commit_count":   len(list(repo.iter_commits())),
        "remote_url":     repo.remotes.origin.url if repo.remotes else None,
        "is_dirty":       repo.is_dirty(untracked_files=True)
    }
