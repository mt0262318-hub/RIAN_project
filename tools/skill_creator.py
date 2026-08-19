import os
from langchain_core.tools import tool

@tool
def create_new_skill(tool_name: str, code: str) -> str:
    """Creates a new Python skill/tool dynamically. Args: tool_name, code"""
    file_path = f"tools/custom_tools/{tool_name}.py"
    try:
        os.makedirs("tools/custom_tools", exist_ok=True)
        with open(file_path, "w") as f:
            f.write(code)
        
        # Syntax check
        compiled_code = compile(code, file_path, 'exec')
        return f"Success: Skill '{tool_name}' created and verified at {file_path}."
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return f"Failed: {e}"
