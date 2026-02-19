# app/utils/docker_executor.py
# Member 2 — System + DevOps + Execution
# Handles: sandboxed code execution using Docker containers

import os
import json
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)

# Docker images to use per language
DOCKER_IMAGES = {
    "python": "python:3.11-slim",
    "javascript": "node:18-slim",
    "default": "python:3.11-slim"
}

# Resource limits for sandboxed containers
CONTAINER_LIMITS = {
    "memory": "512m",
    "cpus": "1.0",
    "timeout": 120  # seconds
}


def is_docker_available() -> bool:
    """Check if Docker daemon is running and accessible."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_in_docker(
    repo_path: str,
    command: list,
    image: str = DOCKER_IMAGES["python"],
    env_vars: dict = None,
    writable: bool = False
) -> dict:
    """
    Execute a shell command inside an isolated Docker container.

    Security features:
      - --network none: no internet access from container
      - --read-only:    root filesystem is read-only
      - --tmpfs /tmp:   writable temp space (100MB limit)
      - --memory:       RAM capped at 512MB
      - --cpus:         CPU limited to 1 core
      - --rm:           auto-remove container after exit

    Args:
        repo_path:  Host path mounted into container at /workspace
        command:    Command list to run inside container (e.g. ["pytest", "-v"])
        image:      Docker image to use
        env_vars:   Optional env vars to inject into container
        writable:   If True, mounts repo as read-write (needed for fix application)

    Returns:
        {
            "stdout": str,
            "stderr": str,
            "exit_code": int,
            "success": bool
        }
    """
    mount_mode = "rw" if writable else "ro"

    docker_cmd = [
        "docker", "run",
        "--rm",                                          # Auto-remove on exit
        "--network", "none",                             # No internet access
        f"--memory={CONTAINER_LIMITS['memory']}",        # Memory limit
        f"--cpus={CONTAINER_LIMITS['cpus']}",            # CPU limit
        "--read-only",                                   # Read-only root FS
        "--tmpfs", "/tmp:size=100m,mode=1777",           # Writable temp
        "--tmpfs", "/root:size=50m",                     # Writable home (for pip cache)
        "-v", f"{os.path.abspath(repo_path)}:/workspace:{mount_mode}",
        "-w", "/workspace",
    ]

    # Inject environment variables if provided
    if env_vars:
        for key, value in env_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])

    docker_cmd.append(image)
    docker_cmd.extend(command)

    logger.info(f"[DOCKER] Running: {' '.join(command[:3])}... in {image}")

    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=CONTAINER_LIMITS["timeout"]
        )

        logger.info(f"[DOCKER] exit_code={result.returncode}")
        if result.stderr:
            logger.debug(f"[DOCKER] stderr: {result.stderr[:200]}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }

    except subprocess.TimeoutExpired:
        logger.error(f"[DOCKER] Container timed out after {CONTAINER_LIMITS['timeout']}s")
        return {
            "stdout": "",
            "stderr": f"Container execution timed out after {CONTAINER_LIMITS['timeout']} seconds",
            "exit_code": -1,
            "success": False
        }
    except FileNotFoundError:
        logger.error("[DOCKER] Docker not found. Falling back to direct execution.")
        return _fallback_run(repo_path, command)


def run_tests_sandboxed(repo_path: str, language: str = "python") -> dict:
    """
    Run tests inside a Docker sandbox. Installs dependencies first.

    For Python: installs requirements.txt, then runs pytest with JSON report.
    For JS:     runs npm install, then jest --json.

    Args:
        repo_path: Local path to cloned repo
        language:  "python" or "javascript"

    Returns:
        {
            "stdout": str,
            "stderr": str,
            "exit_code": int,
            "success": bool,
            "report_json": dict or None   # Parsed JSON report if available
        }
    """
    report_host_path = tempfile.mktemp(suffix=".json")
    report_container_path = "/tmp/test_report.json"

    if language == "python":
        command = [
            "sh", "-c",
            (
                # Install deps silently if requirements.txt exists
                "[ -f requirements.txt ] && pip install -r requirements.txt -q 2>/dev/null || true; "
                # Install pytest-json-report if not present
                "pip install pytest pytest-json-report -q 2>/dev/null; "
                # Run tests with JSON report
                f"python -m pytest --json-report --json-report-file={report_container_path} -v --tb=short 2>&1; "
                # Output the report to stdout so we can capture it
                f"echo '---REPORT_START---'; cat {report_container_path} 2>/dev/null || echo '{{}}'; echo '---REPORT_END---'"
            )
        ]
        image = DOCKER_IMAGES["python"]

    elif language == "javascript":
        command = [
            "sh", "-c",
            (
                "[ -f package.json ] && npm install --silent 2>/dev/null || true; "
                f"npx jest --json --outputFile={report_container_path} --forceExit --no-coverage 2>&1; "
                f"echo '---REPORT_START---'; cat {report_container_path} 2>/dev/null || echo '{{}}'; echo '---REPORT_END---'"
            )
        ]
        image = DOCKER_IMAGES["javascript"]

    else:
        return {"stdout": "", "stderr": f"Unknown language: {language}", "exit_code": 1, "success": False}

    result = run_in_docker(repo_path, command, image=image, writable=False)

    # Extract JSON report from stdout
    report_json = _extract_report_json(result["stdout"])

    return {
        **result,
        "report_json": report_json
    }


def apply_fix_sandboxed(repo_path: str, fix_script: str) -> dict:
    """
    Apply a fix script inside a Docker container with WRITE access to the repo.
    Used by the AI agent to safely apply code fixes.

    Args:
        repo_path:   Local repo path (mounted read-write)
        fix_script:  Python or shell script content to execute

    Returns:
        Standard result dict
    """
    # Write fix script to temp file
    script_path = os.path.join(repo_path, "_ai_agent_fix.py")
    try:
        with open(script_path, "w") as f:
            f.write(fix_script)

        result = run_in_docker(
            repo_path,
            ["python", "_ai_agent_fix.py"],
            image=DOCKER_IMAGES["python"],
            writable=True  # Needs write access to apply fixes
        )
        return result

    finally:
        # Always clean up the fix script
        if os.path.exists(script_path):
            os.remove(script_path)


def run_linter_sandboxed(repo_path: str) -> dict:
    """
    Run flake8 linter inside Docker to detect LINTING issues.
    Outputs in parseable format: file:line:col:code message

    Returns:
        result dict with stdout containing lint warnings
    """
    command = [
        "sh", "-c",
        (
            "pip install flake8 -q 2>/dev/null; "
            "flake8 . --max-line-length=120 --format='%(path)s:%(row)d:%(col)d: %(code)s %(text)s' "
            "--exclude=.git,__pycache__,node_modules,venv,.venv 2>&1 || true"
        )
    ]
    return run_in_docker(repo_path, command, image=DOCKER_IMAGES["python"], writable=False)


# ─── Fallback (no Docker) ───────────────────────────────────────────────────

def _fallback_run(repo_path: str, command: list) -> dict:
    """
    Direct execution fallback when Docker is unavailable.
    WARNING: Not sandboxed. Use only in dev/testing.
    """
    logger.warning("[DOCKER] FALLBACK: Running WITHOUT Docker sandbox (dev mode only)")
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=CONTAINER_LIMITS["timeout"]
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Timed out", "exit_code": -1, "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1, "success": False}


def _extract_report_json(output: str):
    """Extract JSON report embedded between sentinel markers in stdout."""
    try:
        start = output.find("---REPORT_START---")
        end = output.find("---REPORT_END---")
        if start == -1 or end == -1:
            return None
        json_str = output[start + len("---REPORT_START---"):end].strip()
        return json.loads(json_str)
    except (json.JSONDecodeError, Exception):
        return None
