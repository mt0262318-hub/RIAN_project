import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Universal bridge dispatcher with clean output
clean_bridge_engine = """
async def process_and_dispatch_action(text: str):
    q = (text or "").lower().strip()
    if "notepad" in q:
        await safe_bridge_send({"action": "open_app", "target": "notepad"})
        return "Notepad khol diya hai."
    elif "youtube" in q:
        await safe_bridge_send({"action": "open_url", "target": "https://youtube.com"})
        return "YouTube open ho gaya."
    elif "edge" in q or "browser" in q:
        await safe_bridge_send({"action": "open_app", "target": "msedge"})
        return "Microsoft Edge launch kar diya hai."
    elif "cmd" in q or "terminal" in q:
        await safe_bridge_send({"action": "open_app", "target": "cmd"})
        return "Command Prompt ready hai."
    return None

def clean_dashboard_text(text: str) -> str:
    if not isinstance(text, str): return str(text)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"Here\'s a thinking process:.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\\[USER\\].*", "", text, flags=re.DOTALL)
    text = re.sub(r"Output Generation:.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\\*\\*Final Output.*", "", text, flags=re.DOTALL)
    return text.strip()
"""

if "async def process_and_dispatch_action" not in code:
    code = clean_bridge_engine + "\n" + code

# Hook directly inside voice_query_handler
voice_hook = """
        direct_reply = await process_and_dispatch_action(user_text)
        if direct_reply:
            return {"user_text": user_text, "response_text": direct_reply, "audio": None}
"""

if "direct_reply = await process_and_dispatch_action" not in code:
    code = code.replace("user_text = transcription.text.strip()", "user_text = transcription.text.strip()\n" + voice_hook)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Voice Pipeline & OS Dispatcher successfully locked.")
