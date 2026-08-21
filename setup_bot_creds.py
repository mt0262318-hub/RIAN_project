import os

token = "8822708536:AAEKW0rQfAspYA-NaKuka8Tb1k0fdgKRXgY"

# .env file create ya update kar rahe hain
with open(".env", "w") as f:
    f.write(f"TELEGRAM_BOT_TOKEN={token}\n")

print("Token saved to .env successfully!")
