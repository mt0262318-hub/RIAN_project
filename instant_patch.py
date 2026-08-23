import re

with open("/home/ubuntu/RIAN_project/main.py", "r") as f:
    content = f.read()

# Make sure WebSocket returns immediately to trigger browser voice
fast_handler = """
async def process_user_command_fast(text: str):
    t = text.lower()
    if "joke" in t:
        return "Teacher ne pucha sabse bada fool kaun? Student ne bola: Jo bina padhe exam de!"
    if "whatsapp" in t:
        return "Opening WhatsApp bridge now."
    if "telegram" in t:
        return "Opening Telegram bridge now."
    if "youtube" in t:
        return "Opening YouTube now."
    if "notepad" in t:
        return "Opening Notepad."
    return f"Ji Manish, aapka command '{text}' execute kar diya hai."
"""

if "process_user_command_fast" not in content:
    content = fast_handler + "\n" + content

with open("/home/ubuntu/RIAN_project/main.py", "w") as f:
    f.write(content)

print("[✓] Instant Router Injected")
