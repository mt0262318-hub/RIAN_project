import re

# Direct token aur chat id inject kar rahe hain safety_visual_pipeline.py mein
with open("safety_visual_pipeline.py", "r") as f:
    code = f.read()

# Old method replace with explicit fallback
old_block = '''    def send_approval_request_to_telegram(self, image_path, description="New UI Proposal"):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            return False'''

new_block = '''    def send_approval_request_to_telegram(self, image_path, description="New UI Proposal"):
        token = os.getenv("TELEGRAM_BOT_TOKEN") or "7507914035:AAHQv7F6w..." # Yahan apna bot token hai
        chat_id = os.getenv("TELEGRAM_CHAT_ID") or "YOUR_CHAT_ID"'''

# Let's write a robust version directly into safety_visual_pipeline.py
with open("safety_visual_pipeline.py", "w") as f:
    f.write(code.replace(old_block, new_block))

print("Pipeline patched with direct fallback credentials!")
