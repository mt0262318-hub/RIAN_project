import os
import re
import time
import subprocess

print("==> 1. Fixing UI Audio Engine in HTML/JS...")
for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "node_modules" in root:
        continue
    for f in files:
        if f.endswith((".html", ".js")):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8") as file:
                    content = file.read()
                
                # Direct browser speech synthesis fallback if binary audio fails
                if "function playAudio" in content or "playAudio" in content:
                    patch = """
window.playVoiceDirect = function(text, base64Audio) {
    if (base64Audio) {
        try {
            var audio = new Audio("data:audio/mp3;base64," + base64Audio);
            audio.play().catch(function(e) {
                console.log("Base64 Audio blocked, falling back to Web Speech:", e);
                var u = new SpeechSynthesisUtterance(text);
                u.lang = 'hi-IN';
                window.speechSynthesis.speak(u);
            });
            return;
        } catch(err) { console.error(err); }
    }
    if (text && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance(text);
        u.lang = 'hi-IN';
        u.rate = 1.0;
        window.speechSynthesis.speak(u);
    }
};
"""
                    if "playVoiceDirect" not in content:
                        content = content.replace("</head>", f"<script>{patch}</script></head>")
                        with open(p, "w", encoding="utf-8") as file:
                            file.write(content)
                        print(f" -> Patched audio player in: {p}")
            except Exception:
                pass

print("==> 2. Killing stale processes...")
subprocess.run("fuser -k 8501/tcp 2>/dev/null", shell=True)
subprocess.run("pkill -f cloudflared 2>/dev/null", shell=True)
subprocess.run("pkill -f uvicorn 2>/dev/null", shell=True)
time.sleep(1)

print("==> 3. Starting Uvicorn (Auto-Reload mode)...")
os.system("nohup uvicorn main:app --host 0.0.0.0 --port 8501 --reload > server.log 2>&1 &")
time.sleep(3)

print("==> 4. Starting Cloudflare Tunnel...")
cf_proc = subprocess.Popen(
    ["cloudflared", "tunnel", "--url", "http://127.0.0.1:8501"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

url_found = None
start_time = time.time()
while time.time() - start_time < 15:
    line = cf_proc.stdout.readline()
    if not line:
        continue
    match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
    if match:
        url_found = match.group(0)
        break

print("\n" + "="*50)
if url_found:
    print(f"🚀 LIVE UI LINK: {url_found}/ui")
else:
    print("Could not auto-extract URL in 15s. Checking log...")
print("="*50 + "\n")
