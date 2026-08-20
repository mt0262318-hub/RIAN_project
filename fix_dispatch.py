import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Ensure response is clean before sending to frontend / WebSocket
clean_func = """
def clean_llm_output(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    # Remove <think> blocks cleanly
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()
"""

if "def clean_llm_output" not in content:
    content = clean_func + "\n" + content
    # Replace in chat return
    content = content.replace("final_output", "clean_llm_output(final_output)")
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Injected global output cleaner into main.py")
else:
    print("✅ Global cleaner already exists")
