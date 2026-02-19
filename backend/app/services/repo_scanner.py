# app/services/repo_scanner.py 
# Member 2 — Repo Error Scanner 
# Flow: GitHub URL → Clone → Detect All Errors → Return structured report 
# This report is passed directly to Member 1's fixer agent 
 
import os 
import ast 
import re 
import glob 
import json 
import shutil 
import logging 
import subprocess 
import sys 
import tempfile 
 
logger = logging.getLogger(__name__) 
 
 
# ─── Bug type classifier (same labels as hackathon spec) ──────────────────── 
BUG_TYPE_PATTERNS = { 
    "SYNTAX":      [r"SyntaxError", r"invalid syntax", r"unexpected token"], 
    "TYPE_ERROR":  [r"TypeError", r"type error", r"is not a function"], 
    "IMPORT":      [r"ImportError", r"ModuleNotFoundError", r"Cannot find module", r"No module named"], 
    "INDENTATION": [r"IndentationError", r"unexpected indent", r"unindent does not match"], 
    "LINTING":     [r"unused import", r"undefined variable", r"W\d{4}", r"E\d{4}", r"F\d{3}"], 
    "LOGIC":       [r"AssertionError", r"assert", r"Expected.*received", r"FAILED"], 
} 
 
 
def _classify_bug_type(error_text: str) -> str: 
    for bug_type, patterns in BUG_TYPE_PATTERNS.items(): 
        for pattern in patterns: 
            if re.search(pattern, error_text, re.IGNORECASE): 
                return bug_type 
    return "LOGIC" 
 
 
def _extract_line_number(text: str) -> int: 
    for pattern in [r"line (\d+)", r":(\d+):", r", line (\d+)"]: 
        m = re.search(pattern, text, re.IGNORECASE) 
        if m: 
            return int(m.group(1)) 
    return 0 
 
 
# ─── Find source files (not test files) ───────────────────────────────────── 
 
def find_source_files(repo_path: str) -> list: 
    """Find all Python source files, excluding test files and venv.""" 
    all_py = glob.glob(os.path.join(repo_path, "**/*.py"), recursive=True) 
 
    skip = ["test_", "_test.py", "venv", ".venv", "__pycache__", "node_modules", ".git"] 
    source_files = [f for f in all_py if not any(s in f for s in skip)] 
 
    logger.info(f"[SCAN] Found {len(source_files)} source files") 
    return source_files 
 
 
# ─── Static analysis per file ──────────────────────────────────────────────── 
 
def analyze_file(file_path: str, repo_path: str) -> list: 
    """ 
    Run static analysis on a single file. 
    Detects: SYNTAX, INDENTATION, IMPORT, TYPE_ERROR, LINTING errors. 
 
    Returns list of error dicts. 
    """ 
    errors = [] 
    relative = os.path.relpath(file_path, repo_path) 
 
    try: 
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f: 
            source = f.read() 
    except Exception as e: 
        return [{"file": relative, "bug_type": "UNKNOWN", "line": 0, 
                 "description": str(e), "fix_hint": "Cannot read file"}] 
 
    # ── SYNTAX check ──────────────────────────────────────────────────────── 
    try: 
        ast.parse(source) 
    except SyntaxError as e: 
        errors.append({ 
            "file": relative, 
            "bug_type": "SYNTAX", 
            "line": e.lineno or 0, 
            "description": f"SyntaxError: {e.msg}", 
            "fix_hint": f"Fix syntax at line {e.lineno}: {(e.text or '').strip()}" 
        }) 
        return errors  # Can't do more analysis if syntax is broken 
 
    # ── INDENTATION check ──────────────────────────────────────────────────── 
    try: 
        compile(source, file_path, "exec") 
    except IndentationError as e: 
        errors.append({ 
            "file": relative, 
            "bug_type": "INDENTATION", 
            "line": e.lineno or 0, 
            "description": f"IndentationError: {e.msg}", 
            "fix_hint": f"Fix indentation at line {e.lineno}" 
        }) 
        return errors 
 
    # ── IMPORT check (via AST) ─────────────────────────────────────────────── 
    try: 
        tree = ast.parse(source) 
        lines = source.splitlines() 
 
        for node in ast.walk(tree): 
            if isinstance(node, ast.ImportFrom): 
                module = node.module or "" 
                names = [alias.name for alias in node.names] 
                try: 
                    mod = __import__(module, fromlist=names) 
                    for name in names: 
                        if not hasattr(mod, name): 
                            errors.append({ 
                                "file": relative, 
                                "bug_type": "IMPORT", 
                                "line": node.lineno, 
                                "description": f"ImportError: cannot import '{name}' from '{module}'", 
                                "fix_hint": f"'{name}' does not exist in '{module}'" 
                            }) 
                except ImportError as e: 
                    errors.append({ 
                        "file": relative, 
                        "bug_type": "IMPORT", 
                        "line": node.lineno, 
                        "description": f"ImportError: {str(e)}", 
                        "fix_hint": f"Install or remove the import at line {node.lineno}" 
                    }) 
 
            elif isinstance(node, ast.Import): 
                for alias in node.names: 
                    try: 
                        __import__(alias.name) 
                    except ImportError: 
                        errors.append({ 
                            "file": relative, 
                            "bug_type": "IMPORT", 
                            "line": node.lineno, 
                            "description": f"ImportError: No module named '{alias.name}'", 
                            "fix_hint": f"Install '{alias.name}' or remove the import" 
                        }) 
 
        # ── TYPE_ERROR check (string + non-string concatenation) ───────────── 
        for node in ast.walk(tree): 
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add): 
                left, right = node.left, node.right 
                left_str  = isinstance(left,  ast.Constant) and isinstance(left.value,  str) 
                right_str = isinstance(right, ast.Constant) and isinstance(right.value, str) 
 
                if left_str and isinstance(right, ast.Name) and not right_str: 
                    errors.append({ 
                        "file": relative, 
                        "bug_type": "TYPE_ERROR", 
                        "line": node.lineno, 
                        "description": f"TypeError: string + non-string variable '{right.id}'", 
                        "fix_hint": f"Wrap '{right.id}' with str() at line {node.lineno}" 
                    }) 
                elif right_str and isinstance(left, ast.Name) and not left_str: 
                    errors.append({ 
                        "file": relative, 
                        "bug_type": "TYPE_ERROR", 
                        "line": node.lineno, 
                        "description": f"TypeError: non-string variable '{left.id}' + string", 
                        "fix_hint": f"Wrap '{left.id}' with str() at line {node.lineno}" 
                    }) 
 
    except Exception as e: 
        logger.warning(f"[SCAN] AST analysis failed for {relative}: {e}") 
 
    # ── LINTING check (via flake8) ─────────────────────────────────────────── 
    try: 
        flake = subprocess.run( 
            [ 
                sys.executable, "-m", "flake8", 
                "--select=F401,F811,F841",   # unused imports, redefined, unused vars 
                "--format=%(row)d::%(code)s::%(text)s", 
                file_path 
            ], 
            capture_output=True, text=True, timeout=30 
        ) 
 
        for line in flake.stdout.splitlines(): 
            parts = line.strip().split("::") 
            if len(parts) == 3: 
                try: 
                    line_no  = int(parts[0]) 
                    code     = parts[1].strip() 
                    message  = parts[2].strip() 
 
                    # Don't duplicate what IMPORT check already caught 
                    already = any(e["line"] == line_no and e["bug_type"] == "IMPORT" for e in errors) 
                    if not already: 
                        errors.append({ 
                            "file": relative, 
                            "bug_type": "LINTING", 
                            "line": line_no, 
                            "description": f"{code}: {message}", 
                            "fix_hint": f"Remove or use the unused import at line {line_no}" 
                        }) 
                except ValueError: 
                    pass 
    except Exception as e: 
        logger.warning(f"[SCAN] flake8 failed for {relative}: {e}") 
 
    return errors 
 
 
# ─── Pytest for LOGIC errors ───────────────────────────────────────────────── 
 
def detect_logic_errors(repo_path: str) -> list: 
    """ 
    Run pytest to detect LOGIC errors (wrong return values, wrong conditions etc). 
    These can only be caught by running actual tests. 
    """ 
    errors = [] 
 
    test_files = ( 
        glob.glob(os.path.join(repo_path, "**/test_*.py"), recursive=True) + 
        glob.glob(os.path.join(repo_path, "**/*_test.py"), recursive=True) 
    ) 
 
    if not test_files: 
        logger.info("[SCAN] No test files — skipping LOGIC detection") 
        return [] 
 
    logger.info(f"[SCAN] Running pytest for LOGIC errors ({len(test_files)} test files)") 
 
    report_file = os.path.join(tempfile.gettempdir(), "scan_pytest_report.json") 
 
    try: 
        subprocess.run( 
            [ 
                sys.executable, "-m", "pytest", 
                "--tb=short", "-q", 
                "--json-report", 
                f"--json-report-file={report_file}" 
            ], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            timeout=120 
        ) 
    except subprocess.TimeoutExpired: 
        logger.error("[SCAN] pytest timed out") 
        return [] 
    except FileNotFoundError: 
        logger.warning("[SCAN] pytest not found") 
        return [] 
 
    if not os.path.exists(report_file): 
        logger.warning("[SCAN] pytest JSON report not generated") 
        return [] 
 
    try: 
        with open(report_file) as f: 
            report = json.load(f) 
 
        for test in report.get("tests", []): 
            if test["outcome"] in ("failed", "error"): 
                node    = test.get("nodeid", "") 
                file_p  = node.split("::")[0] 
                call    = test.get("call") or test.get("setup") or {} 
                err_txt = call.get("longrepr", "") if isinstance(call, dict) else "" 
                line_no = 0 
                if isinstance(call, dict): 
                    line_no = call.get("crash", {}).get("lineno", 0) 
                if not line_no: 
                    line_no = _extract_line_number(err_txt) 
 
                errors.append({ 
                    "file": file_p, 
                    "bug_type": "LOGIC", 
                    "line": line_no, 
                    "description": f"Test failed: {err_txt[:200].strip()}", 
                    "fix_hint": f"Fix logic error in {file_p} at line {line_no}" 
                }) 
 
    except Exception as e: 
        logger.error(f"[SCAN] Failed to parse pytest report: {e}") 
    finally: 
        if os.path.exists(report_file): 
            os.remove(report_file) 
 
    return errors 
 
 
# ─── Main scan function ─────────────────────────────────────────────────────── 
 
def scan_repo(repo_path: str, repo_url: str = "") -> dict: 
    """ 
    Main entry point. 
    Scans a cloned repo and returns a structured error report. 
 
    This report is passed directly to the fixer agent (Member 1). 
 
    Returns: 
        { 
            "repository": str, 
            "total_errors": int, 
            "summary": { "SYNTAX": n, "LOGIC": n, ... }, 
            "errors": [ 
                { 
                    "file": "src/utils.py", 
                    "bug_type": "LINTING", 
                    "line": 1, 
                    "description": "F401: 'os' imported but unused", 
                    "fix_hint": "Remove or use the unused import at line 1" 
                }, 
                ... 
            ] 
        } 
    """ 
    logger.info(f"[SCAN] Starting scan of {repo_path}") 
 
    # 1. Find source files 
    source_files = find_source_files(repo_path) 
 
    # 2. Static analysis on each file 
    all_errors = [] 
    for file_path in source_files: 
        file_errors = analyze_file(file_path, repo_path) 
        if file_errors: 
            rel = os.path.relpath(file_path, repo_path) 
            logger.info(f"[SCAN] {rel}: {len(file_errors)} error(s)") 
        all_errors.extend(file_errors) 
 
    # 3. Pytest for LOGIC errors 
    logic_errors = detect_logic_errors(repo_path) 
    all_errors.extend(logic_errors) 
 
    # 4. Build summary 
    summary = { 
        "SYNTAX":      len([e for e in all_errors if e["bug_type"] == "SYNTAX"]), 
        "INDENTATION": len([e for e in all_errors if e["bug_type"] == "INDENTATION"]), 
        "IMPORT":      len([e for e in all_errors if e["bug_type"] == "IMPORT"]), 
        "LINTING":     len([e for e in all_errors if e["bug_type"] == "LINTING"]), 
        "TYPE_ERROR":  len([e for e in all_errors if e["bug_type"] == "TYPE_ERROR"]), 
        "LOGIC":       len([e for e in all_errors if e["bug_type"] == "LOGIC"]), 
    } 
 
    report = { 
        "repository": repo_url or repo_path, 
        "total_errors": len(all_errors), 
        "summary": summary, 
        "errors": all_errors   # ← Pass this to Member 1's fixer agent 
    } 
 
    logger.info(f"[SCAN] Complete — {len(all_errors)} total errors found") 
    logger.info(f"[SCAN] Summary: {summary}") 
 
    return report 