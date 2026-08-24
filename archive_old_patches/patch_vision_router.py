import re
import json

with open("main.py", "r") as f:
    content = f.read()

# Auto-play bypass inject: Direct video watch link execute kare
fix_logic = '''
    if "gana" in prompt.lower() or "song" in prompt.lower() or "play" in prompt.lower():
        # Clean song name
        song_query = re.sub(r'(play|chalao|suno|gana|song|lagao|on youtube)', '', prompt, flags=re.IGNORECASE).strip()
        return {"action": "play_youtube", "params": {"query": song_query}}
'''

print("Patching vision & action router...")
