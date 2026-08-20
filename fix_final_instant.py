import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Universal bridge action executor
action_block = '''
async def handle_direct_action(txt: str):
    t = (txt or "").lower().strip()
    if "notepad" in t:
        await manager.broadcast({"action": "open_app", "target": "notepad"})
        return "Notepad khol raha hoon."
    elif "youtube" in t:
        await manager.broadcast({"action": "open_url", "target": "https://youtube.com"})
        return "YouTube open ho gaya."
    elif "edge" in t or "browser" in t:
        await manager.broadcast({"action": "open_app", "target": "msedge"})
        return "Microsoft Edge launch ho raha hai."
    elif "cmd" in t or "terminal" in t:
        await manager.broadcast({"action": "open_app", "target": "cmd"})
        return "Command Prompt ready hai."
    return None
'''

if "async def handle_direct_action" not in code:
    code = action_block + "\n" + code

# Clean response sanitizer
cleaner = '''
def clean_response(text: str) -> str:
    if not isinstance(text, str): return str(text)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"\\[USER\\].*", "", text, flags=re.DOTALL)
    text = re.sub(r"Output Generation:.*", "", text, flags=re.DOTALL)
    return text.strip()
'''
if "def clean_response" not in code:
    code = cleaner + "\n" + code

# Route chat query directly
replacement = """
    direct_act = await handle_direct_action(query or message or "")
    if direct_act:
        return {"status": "success", "user_id": user_id, "response": direct_act}
"""

if "direct_act = await handle_direct_action" not in code:
    code = code.replace("async def chat_endpoint(", "async def chat_endpoint(" + "\n" + replacement)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Instant Bridge Action Dispatcher Installed.")
