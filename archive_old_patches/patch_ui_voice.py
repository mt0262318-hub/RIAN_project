import os, glob

# Find UI html file
html_files = glob.glob("/home/ubuntu/RIAN_project/**/index.html", recursive=True) + glob.glob("/home/ubuntu/RIAN_project/**/ui.html", recursive=True)

js_patch = """
<script>
// Direct Instant Web Speech Synthesis Engine
function speakDirect(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = 'hi-IN';
    window.speechSynthesis.speak(utterance);
}

// Hook into WebSocket messages directly
const origWebSocket = window.WebSocket;
window.WebSocket = function(url, protocols) {
    const ws = new origWebSocket(url, protocols);
    ws.addEventListener('message', function(event) {
        try {
            const data = JSON.parse(event.data);
            const reply = data.text || data.response || data.message || data.voice_text;
            if (reply) {
                console.log("[RIAN Voice Active]:", reply);
                speakDirect(reply);
            }
        } catch(e) {}
    });
    return ws;
};
</script>
"""

for hfile in html_files:
    with open(hfile, "r") as f:
        content = f.read()
    if "speakDirect" not in content and "</body>" in content:
        content = content.replace("</body>", js_patch + "\n</body>")
        with open(hfile, "w") as f:
            f.write(content)
        print(f"[✓] Patched UI file: {hfile}")

