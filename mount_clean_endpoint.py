main_path = "/home/ubuntu/RIAN_project/main.py"
with open(main_path, "r") as f:
    code = f.read()

# Remove misplaced top declarations
code = code.replace("""from pydantic import BaseModel
from fastapi.responses import JSONResponse

class UserCommandReq(BaseModel):
    text: str = ""
    command: str = ""

@app.post("/api/command")
async def execute_user_api_cmd(req: UserCommandReq):
    query = req.text or req.command or "hello"
    from agentic_core import orchestrator
    res = orchestrator.plan_and_execute(query)
    reply = res.get("response", "Command executed.")
    return JSONResponse(content={
        "status": "success",
        "response": reply,
        "text": reply,
        "voice_text": reply
    })
""", "")

clean_route = """
from pydantic import BaseModel
from fastapi.responses import JSONResponse

class UserCommandReq(BaseModel):
    text: str = ""
    command: str = ""

@app.post("/api/command")
async def execute_user_api_cmd(req: UserCommandReq):
    query = req.text or req.command or "hello"
    from agentic_core import orchestrator
    res = orchestrator.plan_and_execute(query)
    reply = res.get("response", "Command executed.")
    return JSONResponse(content={
        "status": "success",
        "response": reply,
        "text": reply,
        "voice_text": reply
    })
"""

# Append cleanly at the end where app is already initialized
code += "\n" + clean_route

with open(main_path, "w") as f:
    f.write(code)

print("[✓] Correctly mounted /api/command after app initialization.")
