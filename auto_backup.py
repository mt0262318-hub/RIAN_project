import subprocess
import os
from datetime import datetime
from tools.vault_storage import upload_file, send_alert

def create_and_upload_backups():
    timestamp = datetime.now().strftime("%Y%m%d_%HuM%S")
    dump_filename = f"rian_backup_{timestamp}.sql.gz"
    
    print("Ⱡ Generating PostgreSQL database dump...")
    
    dump_cmd = f\"docker exec -t rian_postgres pg_dumpall -u postgres | gzip > {dump_filename}\"
    result = subprocess.run(dump_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 or not os.path.exists(dump_filename):
        error_msg = f"❯ *Backup Failed*:\n`{result.stderr}`"
        send_alert(error_msg)
        print(error_msg)
        return False
    
    print(f"☄ Uploading {dump_filename} to Cloud Vault...")
    file_size = round(os.path.getsize(dump_filename) / 1024, 2)
    caption = f"�� *RIAN DB Automated Backup*\n🔥 `
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n▦ Size: {file_size} KB"
    res = upload_file(dump_filename, caption=caption)
    
    if os.path.exists(dump_filename):
        os.remove(dump_filename)
        
    if res.get("ok"):
        print("✅ Backup successfully uploaded to Telegram Vault!")
        return True
    else:
        print("❯ Upload failed:", res)
        return False

if __name__ == "__main__":
    create_and_upload_backups()
