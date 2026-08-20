import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Ensure clean response sanitizer
cleaner_func = """
def sanitize_rian_response(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    # Remove thought blocks and prompt echo
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"(\*\*Draft.*|\*Draft.*|Output Generation:.*|\[USER\].*|\[RIAN\].*)", "", text, flags=re.DOTALL)
    text = text.split("[USER]")[0].split("Output Generation:")[0]
    return text.strip()
"""

if "def sanitize_rian_response" not in code:
    code = cleaner_func + "\n" + code

# 2. Direct PC bridge dispatch before response
bridge_dispatch = """
        # Direct PC Bridge OS Execution
        query_text = (query or message or "").lower().strip()
        if "notepad" in query_text:
            await manager.broadcast({"action": "open_app", "target": "notepad"})
        elif "youtube" in query_text:
            await manager.broadcast({"action": "open_url", "target": "https://youtube.com"})
        elif "edge" in query_text or "browser" in query_text:
            await manager.broadcast({"action": "open_app", "target": "msedge"})
"""

if "Direct PC Bridge OS Execution" not in code:
    if "final_output =" in code:
        code = code.replace("final_output =", bridge_dispatch + "\n        final_output =", 1)

# 3. Clean return
code = re.sub(r'return\s+\{\s*"status":\s*"success",\s*"user_id":\s*user_id,\s*"response":\s*([^\}]+)\}',
              r'return {"status": "success", "user_id": user_id, "response": sanitize_rian_response(\1)}', code)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ main.py completely patched with clean execution & OS bridge triggers.")
