# # app/services/test_runner.py
# # Member 2 — System + DevOps + Execution
# # Handles: auto-discovery of test files, running pytest/jest, parsing failures

# import os
# import json
# import glob
# import subprocess
# import logging
# import tempfile
# import re

# logger = logging.getLogger(__name__)

# # ─── Bug type classifier ────────────────────────────────────────────────────
# # Maps error keywords from pytest/jest output → hackathon-required bug type labels
# BUG_TYPE_PATTERNS = {
#     "SYNTAX":      [r"SyntaxError", r"invalid syntax", r"unexpected token", r"ParseError"],
#     "TYPE_ERROR":  [r"TypeError", r"type error", r"cannot read propert", r"is not a function"],
#     "IMPORT":      [r"ImportError", r"ModuleNotFoundError", r"Cannot find module", r"No module named"],
#     "INDENTATION": [r"IndentationError", r"unexpected indent", r"unindent does not match"],
#     "LINTING":     [r"unused import", r"undefined variable", r"W\d{4}", r"E\d{4}", r"F\d{3}"],
#     "LOGIC":       [r"AssertionError", r"assert", r"Expected.*received", r"FAILED"],
# }


# def _classify_bug_type(error_text: str) -> str:
#     """
#     Classify a test failure into one of the hackathon-required bug types:
#     LINTING | SYNTAX | LOGIC | TYPE_ERROR | IMPORT | INDENTATION
#     """
#     for bug_type, patterns in BUG_TYPE_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, error_text, re.IGNORECASE):
#                 return bug_type
#     return "LOGIC"  # Default fallback


# def _extract_line_number(error_text: str) -> int:
#     """
#     Try to extract a line number from error text.
#     Handles formats like: 'line 15', ':15:', 'Line 15'
#     """
#     patterns = [
#         r'line (\d+)',
#         r':(\d+):',
#         r', line (\d+)',
#         r'Line (\d+)',
#     ]
#     for pattern in patterns:
#         match = re.search(pattern, error_text, re.IGNORECASE)
#         if match:
#             return int(match.group(1))
#     return 0  # Unknown line


# def discover_test_files(repo_path: str) -> dict:
#     """
#     Auto-discover all test files in the repo using glob patterns.
    
#     DISQUALIFICATION RISK: Hardcoded test paths → DQ
#     This function uses recursive glob — never hardcodes paths.

#     Returns:
#         dict with "python" and "javascript" lists of absolute paths
#     """
#     # Python test file conventions
#     py_tests = (
#         glob.glob(os.path.join(repo_path, "**/test_*.py"), recursive=True) +
#         glob.glob(os.path.join(repo_path, "**/*_test.py"), recursive=True) +
#         glob.glob(os.path.join(repo_path, "**/tests/*.py"), recursive=True)
#     )

#     # JavaScript/TypeScript test file conventions
#     js_tests = (
#         glob.glob(os.path.join(repo_path, "**/*.test.js"), recursive=True) +
#         glob.glob(os.path.join(repo_path, "**/*.spec.js"), recursive=True) +
#         glob.glob(os.path.join(repo_path, "**/*.test.ts"), recursive=True) +
#         glob.glob(os.path.join(repo_path, "**/*.spec.ts"), recursive=True)
#     )

#     # Deduplicate
#     py_tests = list(set(py_tests))
#     js_tests = list(set(js_tests))

#     logger.info(f"[DISCOVER] Found {len(py_tests)} Python test files, {len(js_tests)} JS test files")
#     for f in py_tests + js_tests:
#         logger.info(f"  → {os.path.relpath(f, repo_path)}")

#     return {"python": py_tests, "javascript": js_tests}


# def _run_pytest(repo_path: str) -> list:
#     """
#     Run pytest with JSON reporting and parse all failures.

#     Returns:
#         list of failure dicts: {file, bug_type, line, error, test_name}
#     """
#     failures = []
#     report_file = tempfile.mktemp(suffix=".json")

#     try:
#         result = subprocess.run(
#             [
#                 "python", "-m", "pytest",
#                 "--json-report",
#                 f"--json-report-file={report_file}",
#                 "-v",
#                 "--tb=short",        # Short traceback for easier parsing
#                 "--no-header",
#             ],
#             cwd=repo_path,
#             capture_output=True,
#             text=True,
#             timeout=120
#         )

#         logger.info(f"[PYTEST] exit_code={result.returncode}")

#         if not os.path.exists(report_file):
#             # Fallback: parse stdout if JSON report missing
#             logger.warning("[PYTEST] JSON report not generated, parsing stdout")
#             return _parse_pytest_stdout(result.stdout, repo_path)

#         with open(report_file, "r") as f:
#             report = json.load(f)

#         for test in report.get("tests", []):
#             if test["outcome"] in ("failed", "error"):
#                 # Extract details
#                 node_id = test.get("nodeid", "")
#                 file_path = node_id.split("::")[0]  # e.g. src/test_utils.py
#                 test_name = "::".join(node_id.split("::")[1:]) if "::" in node_id else node_id

#                 # Get error text from call or setup phase
#                 call = test.get("call") or test.get("setup") or {}
#                 error_text = call.get("longrepr", "") or call.get("crash", {}).get("message", "")

#                 line = test.get("call", {}).get("crash", {}).get("lineno", 0) if test.get("call") else 0
#                 if not line:
#                     line = _extract_line_number(error_text)

#                 bug_type = _classify_bug_type(error_text)

#                 failures.append({
#                     "file": file_path,
#                     "bug_type": bug_type,
#                     "line": line,
#                     "test_name": test_name,
#                     "error": error_text[:500],  # Truncate for JSON
#                     "status": "Failed"
#                 })

#     except subprocess.TimeoutExpired:
#         logger.error("[PYTEST] Timed out after 120s")
#         failures.append({
#             "file": "unknown",
#             "bug_type": "LOGIC",
#             "line": 0,
#             "test_name": "timeout",
#             "error": "Test run timed out after 120 seconds",
#             "status": "Failed"
#         })
#     except FileNotFoundError:
#         logger.warning("[PYTEST] pytest not installed in target repo")
#     finally:
#         if os.path.exists(report_file):
#             os.remove(report_file)

#     return failures


# def _parse_pytest_stdout(stdout: str, repo_path: str) -> list:
#     """
#     Fallback parser when JSON report unavailable.
#     Parses pytest's plain text output for FAILED lines.
#     """
#     failures = []
#     lines = stdout.splitlines()

#     for line in lines:
#         # Pattern: "FAILED src/test_utils.py::test_something - AssertionError: ..."
#         match = re.match(r'FAILED (.+?)::(.+?) - (.+)', line)
#         if match:
#             file_path = match.group(1).strip()
#             test_name = match.group(2).strip()
#             error_text = match.group(3).strip()

#             failures.append({
#                 "file": file_path,
#                 "bug_type": _classify_bug_type(error_text),
#                 "line": _extract_line_number(error_text),
#                 "test_name": test_name,
#                 "error": error_text[:500],
#                 "status": "Failed"
#             })

#     return failures


# def _run_jest(repo_path: str) -> list:
#     """
#     Run Jest tests and parse failures.

#     Returns:
#         list of failure dicts
#     """
#     failures = []
#     report_file = tempfile.mktemp(suffix=".json")

#     try:
#         result = subprocess.run(
#             [
#                 "npx", "jest",
#                 "--json",
#                 f"--outputFile={report_file}",
#                 "--no-coverage",
#                 "--forceExit"
#             ],
#             cwd=repo_path,
#             capture_output=True,
#             text=True,
#             timeout=120
#         )

#         logger.info(f"[JEST] exit_code={result.returncode}")

#         if not os.path.exists(report_file):
#             logger.warning("[JEST] JSON report not generated")
#             return failures

#         with open(report_file, "r") as f:
#             report = json.load(f)

#         for suite in report.get("testResults", []):
#             file_path = os.path.relpath(suite["testFilePath"], repo_path)

#             for test in suite.get("testResults", []):
#                 if test["status"] == "failed":
#                     error_text = " ".join(test.get("failureMessages", []))

#                     failures.append({
#                         "file": file_path,
#                         "bug_type": _classify_bug_type(error_text),
#                         "line": _extract_line_number(error_text),
#                         "test_name": test.get("fullName", ""),
#                         "error": error_text[:500],
#                         "status": "Failed"
#                     })

#     except subprocess.TimeoutExpired:
#         logger.error("[JEST] Timed out after 120s")
#     except FileNotFoundError:
#         logger.warning("[JEST] npx/jest not found in repo")
#     finally:
#         if os.path.exists(report_file):
#             os.remove(report_file)

#     return failures


# def run_tests(repo_path: str) -> dict:
#     """
#     Main entry point. Discovers and runs all tests (Python + JS).
#     No hardcoded paths — fully dynamic discovery.

#     DISQUALIFICATION RISK: Hardcoded paths → auto-discovery used here.

#     Returns:
#         {
#             "failures": [...],       # List of failure dicts for AI agent
#             "total_passed": int,
#             "total_failed": int,
#             "has_python": bool,
#             "has_javascript": bool,
#             "raw_output": str        # Full combined output for AI analysis
#         }
#     """
#     discovered = discover_test_files(repo_path)
#     all_failures = []
#     passed = 0

#     has_python = len(discovered["python"]) > 0
#     has_javascript = len(discovered["javascript"]) > 0

#     if has_python:
#         py_failures = _run_pytest(repo_path)
#         all_failures.extend(py_failures)
#         logger.info(f"[TEST] Python: {len(py_failures)} failures")
    
#     if has_javascript:
#         js_failures = _run_jest(repo_path)
#         all_failures.extend(js_failures)
#         logger.info(f"[TEST] JS: {len(js_failures)} failures")

#     if not has_python and not has_javascript:
#         logger.warning("[TEST] No test files found in repository")

#     return {
#         "failures": all_failures,
#         "total_passed": passed,
#         "total_failed": len(all_failures),
#         "has_python": has_python,
#         "has_javascript": has_javascript,
#     }

# app/services/test_runner.py 
# Member 2 — System + DevOps + Execution 
# Handles: auto-discovery of test files, running pytest/jest, parsing failures 
 
import os 
import json 
import glob 
import subprocess 
import logging 
import tempfile 
import re 
from app.utils.docker_executor import run_tests_sandboxed
 
logger = logging.getLogger(__name__) 
 
# ─── Bug type classifier ──────────────────────────────────────────────────── 
# Maps error keywords from pytest/jest output → hackathon-required bug type labels 
BUG_TYPE_PATTERNS = { 
    "SYNTAX":      [r"SyntaxError", r"invalid syntax", r"unexpected token", r"ParseError"], 
    "TYPE_ERROR":  [r"TypeError", r"type error", r"cannot read propert", r"is not a function"], 
    "IMPORT":      [r"ImportError", r"ModuleNotFoundError", r"Cannot find module", r"No module named"], 
    "INDENTATION": [r"IndentationError", r"unexpected indent", r"unindent does not match"], 
    "LINTING":     [r"unused import", r"undefined variable", r"W\d{4}", r"E\d{4}", r"F\d{3}"], 
    "LOGIC":       [r"AssertionError", r"assert", r"Expected.*received", r"FAILED"], 
} 
 
 
def _classify_bug_type(error_text: str) -> str: 
    """ 
    Classify a test failure into one of the hackathon-required bug types: 
    LINTING | SYNTAX | LOGIC | TYPE_ERROR | IMPORT | INDENTATION 
    """ 
    for bug_type, patterns in BUG_TYPE_PATTERNS.items(): 
        for pattern in patterns: 
            if re.search(pattern, error_text, re.IGNORECASE): 
                return bug_type 
    return "LOGIC"  # Default fallback 
 
def _parse_json_report_object(report: dict) -> list: #
    """Extracts failure details from a pytest-json-report dictionary."""
    failures = []
    for test in report.get("tests", []): #
        if test["outcome"] in ("failed", "error"): #
            node_id = test.get("nodeid", "") #
            file_path = node_id.split("::")[0] #
            
            call = test.get("call") or test.get("setup") or {} #
            error_text = call.get("longrepr", "") or call.get("crash", {}).get("message", "") #
            line = call.get("crash", {}).get("lineno", 0) #

            failures.append({
                "file": file_path,
                "bug_type": _classify_bug_type(error_text), #
                "line": line or _extract_line_number(error_text), #
                "error": error_text[:500],
                "status": "Failed"
            })
    return failures #
 
def _extract_line_number(error_text: str) -> int: 
    """ 
    Try to extract a line number from error text. 
    Handles formats like: 'line 15', ':15:', 'Line 15' 
    """ 
    patterns = [ 
        r'line (\d+)', 
        r':(\d+):', 
        r', line (\d+)', 
        r'Line (\d+)', 
    ] 
    for pattern in patterns: 
        match = re.search(pattern, error_text, re.IGNORECASE) 
        if match: 
            return int(match.group(1)) 
    return 0  # Unknown line 
 
 
def discover_test_files(repo_path: str) -> dict: 
    """ 
    Auto-discover all test files in the repo using glob patterns. 
     
    DISQUALIFICATION RISK: Hardcoded test paths → DQ 
    This function uses recursive glob — never hardcodes paths. 
 
    Returns: 
        dict with "python" and "javascript" lists of absolute paths 
    """ 
    # Python test file conventions 
    py_tests = ( 
        glob.glob(os.path.join(repo_path, "**/test_*.py"), recursive=True) + 
        glob.glob(os.path.join(repo_path, "**/*_test.py"), recursive=True) + 
        glob.glob(os.path.join(repo_path, "**/tests/*.py"), recursive=True) 
    ) 
 
    # JavaScript/TypeScript test file conventions 
    js_tests = ( 
        glob.glob(os.path.join(repo_path, "**/*.test.js"), recursive=True) + 
        glob.glob(os.path.join(repo_path, "**/*.spec.js"), recursive=True) + 
        glob.glob(os.path.join(repo_path, "**/*.test.ts"), recursive=True) + 
        glob.glob(os.path.join(repo_path, "**/*.spec.ts"), recursive=True) 
    ) 
 
    # Deduplicate 
    py_tests = list(set(py_tests)) 
    js_tests = list(set(js_tests)) 
 
    logger.info(f"[DISCOVER] Found {len(py_tests)} Python test files, {len(js_tests)} JS test files") 
    for f in py_tests + js_tests: 
        logger.info(f"  → {os.path.relpath(f, repo_path)}") 
 
    return {"python": py_tests, "javascript": js_tests} 
 
 
def _run_pytest(repo_path: str) -> list:
    """
    Run pytest with JSON reporting and parse all failures.
    Supports Docker sandboxing if enabled in environment.
    """
    # ─── STEP 1: Check for Docker Sandbox ──────────────────────────────────
    if os.environ.get("USE_DOCKER_SANDBOX") == "true": #
        logger.info(f"[PYTEST] Running in Docker Sandbox for: {repo_path}")
        result = run_tests_sandboxed(repo_path, language="python") #
        
        # If the sandbox successfully generated a JSON report, parse it
        if result.get("report_json"): #
            return _parse_json_report_object(result["report_json"]) #
        
        # If no JSON report, fallback to parsing sandbox stdout
        logger.warning("[PYTEST] Sandbox JSON failed, parsing sandbox stdout")
        return _parse_pytest_stdout(result["stdout"], repo_path) #

    # ─── STEP 2: Existing Local Execution (Fallback/Dev Mode) ──────────────
    failures = []
    report_file = tempfile.mktemp(suffix=".json") #
 
    try: 
        result = subprocess.run(
            ["python", "-m", "pytest", "--json-report", f"--json-report-file={report_file}", "-v", "--tb=short"],
            cwd=repo_path, capture_output=True, text=True, timeout=120
        ) #
 
        if not os.path.exists(report_file): #
            return _parse_pytest_stdout(result.stdout, repo_path) #

        with open(report_file, "r") as f:
            report = json.load(f) #
        
        return _parse_json_report_object(report) # 
 
    except subprocess.TimeoutExpired: 
        logger.error("[PYTEST] Timed out after 120s") 
        failures.append({ 
            "file": "unknown", 
            "bug_type": "LOGIC", 
            "line": 0, 
            "test_name": "timeout", 
            "error": "Test run timed out after 120 seconds", 
            "status": "Failed" 
        }) 
    except FileNotFoundError: 
        logger.warning("[PYTEST] pytest not installed in target repo") 
    finally: 
        if os.path.exists(report_file): 
            os.remove(report_file) 
 
    return failures 
 
 
def _parse_pytest_stdout(stdout: str, repo_path: str) -> list: 
    """ 
    Fallback parser when JSON report unavailable. 
    Parses pytest's plain text output for FAILED lines. 
    """ 
    failures = [] 
    lines = stdout.splitlines() 
 
    for line in lines: 
        # Pattern: "FAILED src/test_utils.py::test_something - AssertionError: ..." 
        match = re.match(r'FAILED (.+?)::(.+?) - (.+)', line) 
        if match: 
            file_path = match.group(1).strip() 
            test_name = match.group(2).strip() 
            error_text = match.group(3).strip() 
 
            failures.append({ 
                "file": file_path, 
                "bug_type": _classify_bug_type(error_text), 
                "line": _extract_line_number(error_text), 
                "test_name": test_name, 
                "error": error_text[:500], 
                "status": "Failed" 
            }) 
 
    return failures 
 
 
def _run_jest(repo_path: str) -> list: 
    """ 
    Run Jest tests and parse failures. 
 
    Returns: 
        list of failure dicts 
    """ 
    failures = [] 
    report_file = tempfile.mktemp(suffix=".json") 
 
    try: 
        result = subprocess.run( 
            [ 
                "npx", "jest", 
                "--json", 
                f"--outputFile={report_file}", 
                "--no-coverage", 
                "--forceExit" 
            ], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            timeout=120 
        ) 
 
        logger.info(f"[JEST] exit_code={result.returncode}") 
 
        if not os.path.exists(report_file): 
            logger.warning("[JEST] JSON report not generated") 
            return failures 
 
        with open(report_file, "r") as f: 
            report = json.load(f) 
 
        for suite in report.get("testResults", []): 
            file_path = os.path.relpath(suite["testFilePath"], repo_path) 
 
            for test in suite.get("testResults", []): 
                if test["status"] == "failed": 
                    error_text = " ".join(test.get("failureMessages", [])) 
 
                    failures.append({ 
                        "file": file_path, 
                        "bug_type": _classify_bug_type(error_text), 
                        "line": _extract_line_number(error_text), 
                        "test_name": test.get("fullName", ""), 
                        "error": error_text[:500], 
                        "status": "Failed" 
                    }) 
 
    except subprocess.TimeoutExpired: 
        logger.error("[JEST] Timed out after 120s") 
    except FileNotFoundError: 
        logger.warning("[JEST] npx/jest not found in repo") 
    finally: 
        if os.path.exists(report_file): 
            os.remove(report_file) 
 
    return failures 
 
 
def run_tests(repo_path: str) -> dict: 
    """ 
    Main entry point. Discovers and runs all tests (Python + JS). 
    No hardcoded paths — fully dynamic discovery. 
 
    DISQUALIFICATION RISK: Hardcoded paths → auto-discovery used here. 
 
    Returns: 
        { 
            "failures": [...],       # List of failure dicts for AI agent 
            "total_passed": int, 
            "total_failed": int, 
            "has_python": bool, 
            "has_javascript": bool, 
            "raw_output": str        # Full combined output for AI analysis 
        } 
    """ 
    discovered = discover_test_files(repo_path) 
    all_failures = [] 
    passed = 0 
 
    has_python = len(discovered["python"]) > 0 
    has_javascript = len(discovered["javascript"]) > 0 
 
    if has_python: 
        py_failures = _run_pytest(repo_path) 
        all_failures.extend(py_failures) 
        logger.info(f"[TEST] Python: {len(py_failures)} failures") 
     
    if has_javascript: 
        js_failures = _run_jest(repo_path) 
        all_failures.extend(js_failures) 
        logger.info(f"[TEST] JS: {len(js_failures)} failures") 
 
    if not has_python and not has_javascript: 
        logger.warning("[TEST] No test files found in repository") 
 
    return { 
        "failures": all_failures, 
        "total_passed": passed, 
        "total_failed": len(all_failures), 
        "has_python": has_python, 
        "has_javascript": has_javascript, 
    }