import re

def parse_error_logs(logs: str):
    """
    Extracts file, line, and bug type. 
    Crucial for 'Test Case Matching' scoring[cite: 59].
    """
    # Regex to capture: file_path:line_number: error_message
    pattern = r"([\w/.-]+\.py):(\d+): ([\w\s:]+)"
    match = re.search(pattern, logs)
    
    if not match:
        return None

    file_path, line_no, error_msg = match.groups()
    
    # Deterministic mapping to PS approved types [cite: 43]
    bug_type = "LINTING"
    if "SyntaxError" in error_msg: bug_type = "SYNTAX"
    elif "ImportError" in error_msg: bug_type = "IMPORT"
    elif "IndentationError" in error_msg: bug_type = "INDENTATION"
    elif "TypeError" in error_msg: bug_type = "TYPE_ERROR"
    elif "AssertionError" in error_msg: bug_type = "LOGIC"
    
    return {
        "file": file_path,
        "line": int(line_no),
        "bug_type": bug_type,
        "message": error_msg.strip()
    }