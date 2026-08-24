import re, glob

# 1. Update main.py websocket router to broadcast immediate agent payload
main_file = "/home/ubuntu/RIAN_project/main.py"
with open(main_file, "r") as f:
    code = f.read()

ws_handler = """
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            import json
            payload = json.loads(data)
            query = payload.get("text", payload.get("command", payload.get("message", "")))
            if query:
                from agentic_core import orchestrator
                res = orchestrator.plan_and_execute(query)
                reply_text = res.get("response", "Command executed.")
                out_pkt = {
                    "type": "agent_response",
                    "status": "completed",
                    "text": reply_text,
                    "response": reply_text,
                    "voice_text": reply_text
                }
                await websocket.send_text(json.dumps(out_pkt))
        except Exception:
            break
"""

# Append / ensure endpoint is registered
if "@app.websocket(\"/ws\")" not in code:
    code += "\n" + ws_handler
    with open(main_file, "w") as f:
        f.write(code)
    print("[✓] WebSocket endpoint synchronized.")
else:
    print("[✓] WebSocket endpoint present.")

# 2. Update all UI files with Web Speech Auto-Speaker & State Reset
ui_files = glob.glob("/home/ubuntu/RIAN_project/**/index.html", recursive=True) + glob.glob("/home/ubuntu/RIAN_project/**/ui.html", recursive=True)

auto_speak_script = """
<script>
window.addEventListener('load', () => {
    function speakText(txt) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(txt);
        u.rate = 1.0;
        u.lang = 'hi-IN';
        window.speechSynthesis.speak(u);
    }

    // Force UI status box unfreeze
    const checkInterval = setInterval(() => {
        const procElem = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.includes('Processing neural command...'));
        if (procElem && window.__last_spoken_text) {
            procElem.textContent = "IDLE - READY";
        }
    }, 500);

    const origWS = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        const ws = new origWS(url, protocols);
        ws.addEventListener('message', (ev) => {
            try {
                const d = JSON.parse(ev.data);
                const txt = d.text || d.response || d.voice_text;
                if (txt) {
                    window.__last_spoken_text = txt;
                    speakText(txt);
                    const procElem = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.includes('Processing neural command...'));
                    if (procElem) procElem.textContent = "READY";
                }
            } catch(e) {}
        });
        return ws;
    };
});
</script>
"""

for uf in ui_files:
    with open(uf, "r") as f:
        c = f.read()
    if "speakText" not in c and "</body>" in c:
        c = c.replace("</body>", auto_speak_script + "\n</body>")
        with open(uf, "w") as f:
            f.write(c)
        print(f"[✓] Synced UI Speech Engine in: {uf}")
