import os
# Updated imports for Mistral v1.0.0+
from mistralai import Mistral 
from app.services.git_services import commit_and_push #

class FixerService:
    def __init__(self, api_key:str):
        # New initialization for v1.0.0
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is missing from environment")
        self.client = Mistral(api_key=api_key)
        self.model = "codestral-latest"

    async def get_repair(self, file_content, error_data):
        """
        Uses Codestral to generate a fix based on test_runner results.
        """
        system_msg = "You are a senior DevOps engineer. Return ONLY the raw corrected code for the file. No explanations. No backticks."
        
        # Mapping teammate's 'error' key to the prompt
        error_log = error_data.get('error', 'No log provided')
        
        user_msg = f"""
        Fix the {error_data['bug_type']} in {error_data['file']} at line {error_data['line']}.
        Description: {error_data.get('description')}
        Hint: {error_data.get('fix_hint')}

        ### ORIGINAL CODE:
        {file_content}
    
        
        ### INSTRUCTION:
        Correct only the error. Return the entire file content.
        """

        # Updated chat call for v1.0.0
        chat_response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        )

        content = chat_response.choices[0].message.content.strip()

        # 🚨 CRITICAL UPDATE: Strip Markdown code blocks if the AI includes them
        if content.startswith("```"):
            # Removes the first line (```python) and the last line (```)
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        return content

    async def apply_and_push_fix(self, repo_path, failure, branch_name, github_token, repo_url, commit_counter):
        """
        Reads file, gets repair from AI, writes it, and pushes via git_services.
        """
        file_path = os.path.join(repo_path, failure['file'])
        
        with open(file_path, 'r') as f:
            original_content = f.read()

        fixed_code = await self.get_repair(original_content, failure)

        with open(file_path, 'w') as f:
            f.write(fixed_code)
            print(f"[DEBUG] Locally healed: {failure['file']} at {file_path}") # Add this

        # Enforces [AI-AGENT] prefix and hackathon branch specs
        result =  commit_and_push(
            repo_path=repo_path,
            branch_name=branch_name,
            commit_message=f"Fixed {failure['bug_type']} in {failure['file']}",
            github_token=github_token,
            repo_url=repo_url
        )

        if result["success"]:
            commit_counter["count"] += 1

        return result