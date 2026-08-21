import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def check_for_approval():
    if not TELEGRAM_TOKEN:
        print("Telegram Token missing!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset=-1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("ok") and data.get("result"):
            latest_update = data["result"][-1]
            message = latest_update.get("message", {})
            chat_id = str(message.get("chat", {}).get("id"))
            text = message.get("text", "").strip().upper()

            # Verify chat ID for security
            if chat_id == str(ALLOWED_CHAT_ID):
                if text == "APPROVE":
                    print("[SUCCESS] Approval received from Telegram! Deploying code...")
                    return True
                elif text == "REJECT":
                    print("[REJECTED] Discarding UI proposal.")
                    return "REJECTED"
    except Exception as e:
        print(f"Error checking updates: {e}")
    return False

if __name__ == "__main__":
    print("Telegram Listener Active. Waiting for 'APPROVE' or 'REJECT' response...")
    while True:
        status = check_for_approval()
        if status is True:
            # Yahan hum live deployment trigger karenge
            print("UI Deployed to production successfully!")
            break
        elif status == "REJECTED":
            print("Proposal discarded safely.")
            break
        time.sleep(5)
