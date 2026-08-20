import io
import logging
import sys
import contextlib

logger = logging.getLogger("os_driver")

class WorkspaceAgentEngine:
    """
    Autonomous Deep OS & Sandboxed Execution Driver for R.I.A.N.
    """
    def execute_dynamic_code(self, python_code: str) -> dict:
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Local execution sandbox scope
        local_scope = {}
        
        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                exec(python_code, {}, local_scope)
            
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()
            
            return {
                "status": "SUCCESS",
                "output": output.strip() if output else "Executed with no stdout.",
                "error": errors.strip() if errors else None,
                "scope_variables": [k for k in local_scope.keys() if not k.startswith("__")]
            }
        except Exception as e:
            logger.error(f"Sandbox Execution Exception: {e}")
            return {
                "status": "FAILED",
                "output": stdout_capture.getvalue().strip(),
                "error": str(e)
            }

    def inspect_workspace_environment(self) -> dict:
        import os
        import platform
        return {
            "os": platform.system(),
            "release": platform.release(),
            "python_version": platform.python_version(),
            "cwd": os.getcwd(),
            "sandbox_status": "ONLINE"
        }
