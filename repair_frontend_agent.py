import re

ui_path = "/home/ubuntu/RIAN_project/templates/index.html"
with open(ui_path, "r") as f:
    html = f.read()

# Remove duplicate injected script blocks at the end
html = re.sub(r'<script>[\s\S]*?speakText[\s\S]*?</script>', '', html)
html = re.sub(r'<script>[\s\S]*?Direct Instant Web Speech[\s\S]*?</script>', '', html)

# Inject clean unified speaker & response listener right before </body>
unified_patch = """
<script>
(function() {
    function speakImmediate(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        window.speechSynthesis.resume();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1.0;
        utter.pitch = 1.0;
        utter.lang = 'hi-IN';
        window.speechSynthesis.speak(utter);
    }

    // Direct fetch fallback and socket listener
    window.addEventListener('load', function() {
        const sendBtn = document.getElementById('sendBtn') || document.querySelector('button');
        const inputField = document.getElementById('commandInput') || document.querySelector('input[type="text"]');
        const statusBox = document.querySelector('.status') || Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.includes('Processing neural'));

        async function triggerAgent(txt) {
            if (!txt) return;
            try {
                const res = await fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: txt, command: txt})
                });
                const data = await res.json();
                const reply = data.text || data.response || data.voice_text || "Command processed.";
                
                // Unfreeze status UI
                document.querySelectorAll('*').forEach(el => {
                    if (el.textContent && el.textContent.includes('Processing neural command...')) {
                        el.textContent = "IDLE - READY";
                    }
                });

                // Play Voice
                speakImmediate(reply);
            } catch(e) {
                console.error("Agent HTTP error:", e);
            }
        }

        if (sendBtn && inputField) {
            sendBtn.onclick = function() {
                const txt = inputField.value.trim();
                if (txt) {
                    triggerAgent(txt);
                }
            };
            inputField.onkeydown = function(e) {
                if (e.key === 'Enter') {
                    const txt = inputField.value.trim();
                    if (txt) {
                        triggerAgent(txt);
                    }
                }
            };
        }
    });
})();
</script>
"""

if "</body>" in html:
    html = html.replace("</body>", unified_patch + "\n</body>")
    with open(ui_path, "w") as f:
        f.write(html)
    print("[✓] Templates/index.html cleanly restored & direct-wired to agent API.")
