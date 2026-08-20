with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Direct OS Action Handler with Bridge Dispatch
bridge_clean_endpoint = """
@app.post("/api/chat")
async def chat_api_clean(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    query = body.get("query") or body.get("message") or ""
    user_id = body.get("session_id") or body.get("user_id") or "user"
    q_low = str(query).lower().strip()
    
    # 1. OS Direct Bridge Triggers
    if "notepad" in q_low:
        await manager.broadcast({"action": "open_app", "target": "notepad"})
        return {"status": "success", "user_id": user_id, "response": "Done. Notepad is opening now."}
    elif "youtube" in q_low:
        await manager.broadcast({"action": "open_url", "target": "https://youtube.com"})
        return {"status": "success", "user_id": user_id, "response": "Opening YouTube."}
    elif "edge" in q_low or "browser" in q_low:
        await manager.broadcast({"action": "open_app", "target": "msedge"})
        return {"status": "success", "user_id": user_id, "response": "Launching Microsoft Edge."}
    elif "cmd" in q_low or "terminal" in q_low:
        await manager.broadcast({"action": "open_app", "target": "cmd"})
        return {"status": "success", "user_id": user_id, "response": "Command Prompt ready."}
        
    # 2. General LLM Fallback
    raw_out = local_llm.generate(query)
    import re
    clean_out = re.sub(r"<think>.*?</think>", "", str(raw_out), flags=re.DOTALL).strip()
    return {"status": "success", "user_id": user_id, "response": clean_out}
"""

import re
code = re.sub(r'@app\.post\("/api/chat"\)[\s\S]*?(?=@app\.|\nif __name__|$)', bridge_clean_endpoint + "\n\n", code, count=1)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Force Bridge Router Applied to /api/chat.")
