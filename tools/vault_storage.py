import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8822708536:AAEKW0rQfAspYAANaKukA8Tb1k0fdgkRXgY")
CHAT_ID = os.getenv("TELEGRAM_VAULT_CHAT_ID", "-1004455097708")

def send_alert(message: str) -> dict:
    """Telegram vault me alert/log bhejta hai."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    return requests.post(url, json=payload).json()

def upload_file(file_path: str, caption: str = "") -> dict:
    """Telegram vault me document/file backup upload karta hai."""
    if not os.path.exists(file_path):
        return {"ok": False, "error": f"File not found: {file_path}"}
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        return requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f}).json()

def upload_photo(photo_path: str, caption: str = "") -> dict:
    """Telegram vault me image upload karta hai."""
    if not os.path.exists(photo_path):
        return {"ok": False, "error": f"Image not found: {photo_path}"}
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as f:
        return requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": f}).json()