import os, time, requests
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
while True:
    try:
        res = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1", timeout=10).json()
        if res.get("ok") and res.get("result"):
            msg = res["result"][-1].get("message", {})
            if str(msg.get("chat", {}).get("id")) == str(CHAT_ID) and msg.get("text", "").strip().upper() == "APPROVE":
                print("[SUCCESS] Approved via Telegram! Deploying...")
                break
    except Exception as e:
        pass
    time.sleep(5)
