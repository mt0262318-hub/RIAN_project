token = "8829480393:AAE3MPZCUybdaAxyd6UGLJvCrT-TYT6qAEs"
with open(".env", "w") as f:
    f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
print("New token configured successfully!")
