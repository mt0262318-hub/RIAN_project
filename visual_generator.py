import os
import requests

def trigger_visual_generation(prompt_text):
    print(f"Generating visual asset for prompt: {prompt_text}")
    
    output_dir = "./vault_output"
    os.makedirs(output_dir, exist_ok=True)
    dummy_image_path = os.path.join(output_dir, "generated_render.png")
    
    # Creating a placeholder render binary for pipeline integration
    with open(dummy_image_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n...") 

    # Auto-sync to Telegram Vault (Zero Server Load)
    success = sync_file_to_telegram(dummy_image_path, caption=f"R.I.A.N. Render: {prompt_text}")
    return success

def sync_file_to_telegram(file_path, caption):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram Vault tokens missing. Cleaning up local file.")
        if os.path.exists(file_path):
            os.remove(file_path)
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, "rb") as f:
        response = requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"document": f})
    
    if response.status_code == 200:
        os.remove(file_path) # Immediate local storage cleanup
        print("Asset successfully synced to Telegram and local copy wiped!")
        return True
    else:
        print(f"Telegram sync failed: {response.text}")
        return False

print("Visual Generator module ready!")
