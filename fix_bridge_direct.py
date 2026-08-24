import re

main_path = "/home/ubuntu/RIAN_project/main.py"
with open(main_path, "r") as f:
    code = f.read()

# Unified Fast-Response Handler for both HTTP POST and WebSocket
bridge_patch = """
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class CommandReq(BaseModel):
    text: str = ""
    command: str = ""

@app.post("/api/command")
@app.post("/command")
@app.post("/chat")
async def handle_agent_http_post(req: CommandReq):
    query = req.text or req.command or "hello"
    from agentic_core import orchestrator
    res = orchestrator.plan_and_execute(query)
    reply = res.get("response", "Command executed successfully.")
    return JSONResponse(content={
        "status": "success",
        "text": reply,
        "response": reply,
        "voice_text": reply,
        "reply": reply
    })
"""

if "/api/command" not in code:
    code += "\n" + bridge_patch
    with open(main_path, "w") as f:
        f.write(code)
    print("[✓] HTTP API Command bridges registered.")

