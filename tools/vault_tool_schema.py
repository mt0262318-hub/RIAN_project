from tools.vault_storage import send_alert, upload_file, upload_photo

VAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_vault_alert",
            "description": "Send urgent alerts, notifications, or logs to the Telegram Cloud Vault.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Markdown formatted message to send."}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_file_to_vault",
            "description": "Upload a generated file, code script, or document to the Telegram Cloud Vault.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Server path of the file."},
                    "caption": {"type": "string", "description": "Description of the file."}
                },
                "required": ["file_path"]
            }
        }
    }
]

def handle_vault_call(function_name: str, arguments: dict):
    if function_name == "send_vault_alert":
        return send_alert(arguments.get("message", ""))
    elif function_name == "upload_file_to_vault":
        return upload_file(arguments.get("file_path", ""), arguments.get("caption", ""))
    elif function_name == "upload_photo_to_vault":
        return upload_photo(arguments.get("photo_path", ""), arguments.get("caption", ""))
    return {"error": f"Function {function_name} not found"}
