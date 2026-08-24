import re

main_path = "/home/ubuntu/RIAN_project/main.py"
with open(main_path, "r") as f:
    code = f.read()

# Replace any existing @app.websocket("/ws/telemetry") block completely
new_ws = """
@app.websocket("/ws/telemetry")
async def ws_telemetry_loop(websocket: WebSocket):
    await websocket.accept()
    import json, asyncio
    from agentic_core import orchestrator

    async def log_heartbeat():
        while True:
            try:
                await websocket.send_text(json.dumps({"type": "telemetry", "status": "active"}))
                await asyncio.sleep(2)
            except Exception:
                break

    asyncio.create_task(log_heartbeat())

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
                pkt_out = {
                    "type": "agent_response",
                    "text": reply,
                    "response": reply,
                    "voice_text": reply,
                    "status": "ready"
                }
                await websocket.send_text(json.dumps(pkt_out))
        except Exception:
            break
"""

# If endpoint exists, replace it, else append
pattern = r'@app\.websocket\("/ws/telemetry"\)[\s\S]*?(?=\n@app|\Z)'
if re.search(pattern, code):
    code = re.sub(pattern, new_ws, code)
    print("[✓] Overwrote existing /ws/telemetry with bidirectional agent handler.")
else:
    code += "\n" + new_ws
    print("[✓] Appended bidirectional /ws/telemetry handler.")

with open(main_path, "w") as f:
    f.write(code)

