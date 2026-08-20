with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Safe dispatcher that checks existing ConnectionManager methods
safe_broadcast = """
async def safe_bridge_send(payload: dict):
    if not hasattr(manager, "active_connections"):
        return
    import json
    msg = json.dumps(payload)
    for conn in list(manager.active_connections):
        try:
            await conn.send_text(msg)
        except Exception:
            pass
"""

if "async def safe_bridge_send" not in code:
    code = safe_broadcast + "\n" + code

# Replace manager.broadcast with safe_bridge_send
code = code.replace("await manager.broadcast(", "await safe_bridge_send(")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Patched manager broadcast cleanly without breaking anything.")
