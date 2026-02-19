# app/agents/analyzer_agent.py
class AnalyzerAgent:
    def process_logs(self, failure_data): # Renamed to match orchestrator
        """
        Processes the raw failure data from the scanner.
        If no failure data is provided, it returns None.
        """
        if not failure_data:
            return None #
            
        # Ensure it returns the dictionary format the orchestrator expects
        return failure_data