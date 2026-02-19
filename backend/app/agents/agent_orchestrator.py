from .analyzer_agent import AnalyzerAgent
from .debugger_agent import DebuggerAgent
from .fixer_agent import FixerAgent

class AgentOrchestrator:
    def __init__(self, mistral_api_key):
        self.analyzer = AnalyzerAgent()
        self.debugger = DebuggerAgent()
        # Connects the Codestral service to the Fixer Agent
        self.fixer = FixerAgent(mistral_api_key) 

    async def run_iteration(self, repo_path, logs):
        # 1. Analyzer Agent: Parse logs from Member 3 [cite: 13-15]
        error_data = self.analyzer.process_logs(logs)
        if not error_data:
            return None # Tests passed
        
        # 2. Fixer Agent: Call Codestral and rewrite file [cite: 15-16]
        fix_info = await self.fixer.execute_fix(repo_path, error_data)
        
        # 3. Debugger Agent: Create the Dashboard string for the Judges [cite: 63]
        # Required format: "TYPE error in file line X -> Fix: summary"
        summary = f"Codestral applied {error_data['bug_type'].lower()} patch"
        fix_info["dashboard_output"] = self.debugger.get_dashboard_output(error_data, summary)
        
        # Add metadata for results.json
        fix_info.update(error_data)
        return fix_info