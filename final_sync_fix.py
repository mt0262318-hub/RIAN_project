import re

# 1. Backend main.py me /api/command endpoint register karo
main_path = "/home/ubuntu/RIAN_project/main.py"
with open(main_path, "r") as f:
    main_code = f.read()

endpoint_code = """
from pydantic import BaseModel
from fastapi.responses import JSONResponse

class UserCommandReq(BaseModel):
    text: str = ""
    command: str = ""

@app.post("/api/command")
async def execute_user_api_cmd(req: UserCommandReq):
    query = req.text or req.command or "hello"
    from agentic_core import orchestrator
    res = orchestrator.plan_and_execute(query)
    reply = res.get("response", "Command executed.")
    return JSONResponse(content={
        "status": "success",
        "response": reply,
        "text": reply,
        "voice_text": reply
    })
"""

if "@app.post(\"/api/command\")" not in main_code:
    main_code = endpoint_code + "\n" + main_code
    with open(main_path, "w") as f:
        f.write(main_code)
    print("[✓] Backend /api/command endpoint injected.")

# 2. templates/index.html me exact ID userInput aur sendBtn par direct click bind karo
ui_path = "/home/ubuntu/RIAN_project/templates/index.html"
with open(ui_path, "r") as f:
    html = f.read()

clean_script = """
<script>
window.addEventListener('DOMContentLoaded', () => {
    const inputEl = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    function speakHindi(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        window.speechSynthesis.resume();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1.0;
        utter.lang = 'hi-IN';
        window.speechSynthesis.speak(utter);
    }

    async function sendQuery() {
        if (!inputEl) return;
        const val = inputEl.value.trim();
        if (!val) return;
        
        // Update input display
        inputEl.value = '';
        
        try {
            const resp = await fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: val})
            });
            const data = await resp.json();
            const replyText = data.response || data.text || "Command executed.";
            
            // Clear processing text across UI
            document.querySelectorAll('*').forEach(el => {
                if (el.children.length === 0 && el.textContent.includes('Processing neural')) {
                    el.textContent = "READY";
                }
            });

            // Speak response
            speakHindi(replyText);
        } catch(err) {
            console.error(err);
        }
    }

    if (sendBtn) sendBtn.onclick = (e) => { e.preventDefault(); sendQuery(); };
    if (inputEl) inputEl.onkeydown = (e) => { if (e.key === 'Enter') { e.preventDefault(); sendQuery(); } };
});
</script>
"""

if "speakHindi" not in html:
    html = html.replace("</body>", clean_script + "\n</body>")
    with open(ui_path, "w") as f:
        f.write(html)
    print("[✓] Frontend event binding updated with exact #userInput element.")

