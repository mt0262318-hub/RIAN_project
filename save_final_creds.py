token = "8816425398:AAECsNvkwhPwtnh3V0TFsvLGtTcKrja2ZEA"
chat_id = "7907445261"

with open(".env", "w") as f:
    f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
    f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")

print("Token and Chat ID successfully saved to .env!")
