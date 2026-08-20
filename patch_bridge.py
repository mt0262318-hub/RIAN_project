import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Uvicorn default port inside file to 8501
code = code.replace("port=8000", "port=8501")

# 2. Add Direct PC Bridge Dispatch Trigger before LLM generation
bridge_trigger = """
        # Direct PC Action Bridge Trigger
        q_lower = query.lower() if isinstance(query, str) else ""
        if "notepad" in q_lower:
            await manager.broadcast({"type": "execute", "action": "open_app", "target": "notepad"})
        elif "youtube" in q_lower:
            await manager.broadcast({"type": "execute", "action": "open_url", "target": "https://youtube.com"})
        elif "edge" in q_lower or "browser" in q_lower:
            await manager.broadcast({"type": "execute", "action": "open_app", "target": "msedge"})
"""

if "await manager.broadcast" not in code:
    code = code.replace("final_output = local_llm.generate", bridge_trigger + "\n        final_output = local_llm.generate")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Bridge dispatcher & port 8501 configured in main.py")
