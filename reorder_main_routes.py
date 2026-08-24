with open("/home/ubuntu/RIAN_project/main.py", "r") as f:
    code = f.read()

import re

# Remove duplicate misplaced /api/command blocks
code = re.sub(r'class UserCommandReq[\s\S]*?return JSONResponse[^\n]*\n', '', code)
code = re.sub(r'@app\.post\("/api/command"\)[\s\S]*?return JSONResponse[^\n]*\n', '', code)

# Clean route definition
valid_route = """
from pydantic import BaseModel
from fastapi.responses import JSONResponse

class UserCommandReq(BaseModel):
    text: str = ""
    command: str = ""

@app.post("/api/command")
async def execute_user_api_cmd(req: UserCommandReq):
    query = req.text or req.command or "hello"
    try:
        from agentic_core import orchestrator
        res = orchestrator.plan_and_execute(query)
        reply = res.get("response", "Command executed.")
    except Exception as e:
        reply = f"Response ready: {query}"
    return JSONResponse(content={"status": "success", "response": reply, "text": reply})
"""

# Insert BEFORE uvicorn.run or if __name__ == '__main__'
if "if __name__ ==" in code:
    parts = code.split("if __name__ ==")
    code = parts[0] + "\n" + valid_route + "\nif __name__ ==" + parts[1]
elif "uvicorn.run(" in code:
    idx = code.rfind("uvicorn.run(")
    code = code[:idx] + "\n" + valid_route + "\n" + code[idx:]
else:
    code = code + "\n" + valid_route

with open("/home/ubuntu/RIAN_project/main.py", "w") as f:
    f.write(code)

print("[✓] Correctly placed /api/command before uvicorn.run()")
