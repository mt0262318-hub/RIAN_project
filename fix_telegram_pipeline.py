import os

with open("safety_visual_pipeline.py", "r") as f:
    code = f.read()

# Replace environment lookup with direct hardcoded or fallback values if needed, 
# or let's inspect and fix send_approval_request_to_telegram method.
fixed_code = code.replace(
    '''    def send_approval_request_to_telegram(self, image_path, description="New UI Proposal"):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")''',
    '''    def send_approval_request_to_telegram(self, image_path, description="New UI Proposal"):
        token = os.getenv("TELEGRAM_BOT_TOKEN") or "7507914035:AAHQv7F6w-..." # Apna active token yahan dalo ya env se lo
        chat_id = os.getenv("TELEGRAM_CHAT_ID") or "YOUR_CHAT_ID"'''
)

print("Let's check current environment variables in terminal first.")
