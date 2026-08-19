import requests

BOT_TOKEN = "8822708536:AAEKW0rQfAspYAANaKukA8Tb1k0fdgkRXgY"
CHAT_ID = "-1004455097708"

def send_vault_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    print("Testing connection to RIAN Cloud Vault...")
    res = send_vault_message("🚀 *RIAN Vault Initialized* | Cloud Storage Connected!")
    print("Response:", res)
