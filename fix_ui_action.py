with open("/home/ubuntu/RIAN_project/main.py", "r") as f:
    content = f.read()

# Fix the JavaScript sending logic inside main.py
js_patch = """
<script>
window.addEventListener('DOMContentLoaded', () => {
    const input = document.querySelector('input[type="text"]') || document.getElementById('user-input') || document.querySelector('input');
    const btn = document.querySelector('button') || document.getElementById('send-btn');
    const statusLabel = document.querySelector('.status-text') || document.getElementById('status') || document.querySelector('div[id*="status"]');

    function speakText(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'hi-IN';
            utter.rate = 1.0;
            window.speechSynthesis.speak(utter);
        }
    }

    async function sendCommand() {
        if (!input || !input.value.trim()) return;
        const query = input.value.trim();
        input.value = '';
        if (statusLabel) statusLabel.innerText = "THINKING...";

        try {
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: query, command: query})
            });
            const data = await res.json();
            const reply = data.response || data.text || "Command executed.";
            if (statusLabel) statusLabel.innerText = "SPEAKING: " + reply.substring(0, 30) + "...";
            speakText(reply);
        } catch(e) {
            console.error(e);
            if (statusLabel) statusLabel.innerText = "ERROR PROCESSING";
        }
    }

    if (btn) {
        btn.onclick = (e) => { e.preventDefault(); sendCommand(); };
    }
    if (input) {
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendCommand();
            }
        };
    }
});
</script>
</body>
"""

if "</body>" in content and "sendCommand()" not in content:
    content = content.replace("</body>", js_patch)
    with open("/home/ubuntu/RIAN_project/main.py", "w") as f:
        f.write(content)
    print("[✓] UI Frontend Event Handler Injected.")
else:
    print("[✓] Already present or custom injection.")
