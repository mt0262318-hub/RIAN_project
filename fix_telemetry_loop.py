import re

main_path = "/home/ubuntu/RIAN_project/main.py"
with open(main_path, "r") as f:
    code = f.read()

# Intercept /ws/telemetry to execute agentic command immediately on user message
hook_code = """
@app.websocket("/ws/telemetry")
async def ws_telemetry_agent_bridge(websocket: WebSocket):
    await websocket.accept()
    from agentic_core import orchestrator
    import json
    while True:
        try:
            data = await websocket.receive_text()
            user_text = ""
            try:
                pkt = json.loads(data)
                user_text = pkt.get("text") or pkt.get("command") or pkt.get("message") or ""
            except Exception:
                user_text = data.strip()
            
            if user_text:
                res = orchestrator.plan_and_execute(user_text)
                reply = res.get("response", "Command processed.")
                # Broadcast back to UI
                await websocket.send_text(json.dumps({
                    "type": "agent_response",
                    "text": reply,
                    "response": reply,
                    "voice_text": reply,
                    "status": "ready"
                }))
        except Exception:
            break
"""

# Replace or insert active handler
if "@app.websocket(\"/ws/telemetry\")" not in code:
    code += "\n" + hook_code
    with open(main_path, "w") as f:
        f.write(code)
    print("[✓] Hooked into /ws/telemetry WebSocket.")
else:
    print("[✓] WebSocket handler already configured.")

