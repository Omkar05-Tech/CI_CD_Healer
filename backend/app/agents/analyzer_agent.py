from app.services.test_runner import run_tests #

class AnalyzerAgent:
    def analyze(self, repo_path):
        # Run real discovery and tests instead of just parsing static logs
        results = run_tests(repo_path) #
        return results["failures"] #