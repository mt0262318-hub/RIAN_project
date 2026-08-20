import re

# 1. Update main.py to handle both API payload & direct WebSocket execution
with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Universal bridge router
router_code = """
async def execute_bridge_action(raw_text: str):
    txt = (raw_text or "").lower()
    if "notepad" in txt:
        await manager.broadcast({"action": "open_app", "target": "notepad"})
        return "Opening Notepad for you."
    elif "youtube" in txt:
        await manager.broadcast({"action": "open_url", "target": "https://youtube.com"})
        return "Opening YouTube now."
    elif "edge" in txt or "browser" in txt:
        await manager.broadcast({"action": "open_app", "target": "msedge"})
        return "Opening Microsoft Edge."
    elif "cmd" in txt or "terminal" in txt:
        await manager.broadcast({"action": "open_app", "target": "cmd"})
        return "Launching Terminal."
    return None
"""

if "async def execute_bridge_action" not in code:
    code = router_code + "\n" + code

# Inject execution inside chat endpoint
if "await execute_bridge_action" not in code:
    code = code.replace(
        "final_output = local_llm.generate",
        "action_reply = await execute_bridge_action(query or message or '')\n        if action_reply:\n            final_output = action_reply\n        else:\n            final_output = local_llm.generate"
    )

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Auto-Repair: Router and Direct Dispatch Configured.")
