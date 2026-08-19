import subprocess
import tempfile
import os

class CodeSandbox:
    def __init__(self, timeout_sec: int = 15):
        self.timeout_sec = timeout_sec

    def execute_python(self, code_str: str) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp_file:
            temp_file.write(code_str)
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                ["/home/ubuntu/RIAN_project/venv/bin/python3", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Execution timed out after {self.timeout_sec}s"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def execute_bash(self, command_str: str) -> dict:
        try:
            result = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd="/home/ubuntu/RIAN_project"
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {self.timeout_sec}s"}
        except Exception as e:
            return {"error": str(e)}

sandbox = CodeSandbox()
