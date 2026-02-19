class DebuggerAgent:
    ALLOWED_TYPES = ["LINTING", "SYNTAX", "LOGIC", "TYPE_ERROR", "IMPORT", "INDENTATION"] #

    def validate_and_format(self, failure):
        # Ensure the bug_type is one of the allowed strings
        if failure['bug_type'] not in self.ALLOWED_TYPES: #
            failure['bug_type'] = "LOGIC" #
        return failure