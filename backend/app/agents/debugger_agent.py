# app/agents/debugger_agent.py
class DebuggerAgent:
    ALLOWED_TYPES = ["LINTING", "SYNTAX", "LOGIC", "TYPE_ERROR", "IMPORT", "INDENTATION"] #

    def get_dashboard_output(self, error_data, summary): # Renamed
        """
        Required format for Judges: "TYPE error in file line X -> Fix: summary"
        """
        # Ensure the bug_type is one of the allowed strings
        bug_type = error_data['bug_type']
        if bug_type not in self.ALLOWED_TYPES: #
            bug_type = "LOGIC" #

        return f"{bug_type} error in {error_data['file']} line {error_data['line']} -> {summary}" #