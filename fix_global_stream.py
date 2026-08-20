import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Global Sanitizer & OS Trigger that applies everywhere
global_hook = """
async def process_user_query_globally(query_text: str):
    q = (query_text or "").lower().strip()
    # Trigger Local PC Bridge
    if "notepad" in q:
        await safe_bridge_send({"action": "open_app", "target": "notepad"})
        return "Done. Notepad is opening now."
    elif "youtube" in q:
        await safe_bridge_send({"action": "open_url", "target": "https://youtube.com"})
        return "Opening YouTube."
    elif "edge" in q or "browser" in q:
        await safe_bridge_send({"action": "open_app", "target": "msedge"})
        return "Launching Microsoft Edge."
    elif "cmd" in q or "terminal" in q:
        await safe_bridge_send({"action": "open_app", "target": "cmd"})
        return "Terminal ready."
    return None
"""

if "async def process_user_query_globally" not in code:
    code = global_hook + "\n" + code

# 2. Hard clean any thinking output before sending to WebSocket / UI
clean_patch = """
def strip_all_thinking(text: str) -> str:
    if not isinstance(text, str): return str(text)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"Here\'s a thinking process:.*?(?=\\n\\n|[A-Z][a-z]+:|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"\\*\\*[0-9]\\..*?\\*\\*", "", text)
    return text.strip()
"""
if "def strip_all_thinking" not in code:
    code = clean_patch + "\n" + code

# 3. Hook into WebSocket endpoint / Voice Handler
code = code.replace("await websocket.send_text(response)", "await websocket.send_text(strip_all_thinking(response))")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Global OS router & UI cleaner applied.")
