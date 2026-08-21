with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean up previous broken mobile injections
code = re.sub(r'<style>[\s\S]*?#strict-mobile-shell[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?strict-mobile-shell[\s\S]*?</script>', '', code)

# Surgical Clean Mobile CSS & HTML Injection
surgical_patch = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    body {
        background: #000 !important;
        margin: 0 !important;
        padding: 10px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    /* Hide old duplicate desktop inputs on mobile */
    body > form, body > div:not(#strict-mobile-shell), .input-container {
        display: none !important;
    }

    /* Exact Gorgeous Glassmorphism Bottom Box matching 120917.png */
    .mobile-glass-card {
        background: rgba(0, 15, 20, 0.75) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(0, 255, 204, 0.75) !important;
        border-radius: 14px !important;
        padding: 14px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2) !important;
        margin-top: 15px !important;
    }

    .mobile-listening-msg {
        font-family: monospace !important;
        font-size: 11px !important;
        color: #00ffcc !important;
        text-align: center !important;
        line-height: 1.4 !important;
        font-weight: bold !important;
        letter-spacing: 0.5px !important;
    }

    .mobile-input-row {
        display: flex !important;
        gap: 10px !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .mobile-input-wrapper {
        flex: 1 !important;
        height: 42px !important;
        background: rgba(0, 5, 10, 0.85) !important;
        border: 1px solid rgba(0, 255, 204, 0.6) !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 12px !important;
        box-sizing: border-box !important;
    }

    .mobile-input-wrapper input {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        font-size: 12px !important;
        outline: none !important;
    }

    .mobile-input-wrapper input::placeholder {
        color: rgba(0, 255, 204, 0.45) !important;
    }

    .mobile-mic-svg {
        width: 18px !important;
        height: 18px !important;
        fill: #00ffcc !important;
        flex-shrink: 0 !important;
        margin-left: 8px !important;
        cursor: pointer !important;
        filter: drop-shadow(0 0 3px rgba(0,255,204,0.6)) !important;
    }

    .mobile-send-button {
        height: 42px !important;
        background: rgba(0, 136, 136, 0.9) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 0 18px !important;
        font-family: monospace !important;
        font-size: 13px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        box-shadow: 0 0 10px rgba(0, 255, 204, 0.35) !important;
    }
}
</style>

<script>
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        if (!document.getElementById('mobile-surgical-box')) {
            const container = document.body;
            
            const card = document.createElement('div');
            card.id = 'mobile-surgical-box';
            card.className = 'mobile-glass-card';
            card.innerHTML = `
                <div class="mobile-listening-msg">
                    LISTENING...<br>
                    <span style="font-size: 90%; font-weight: normal; opacity: 0.85;">(Continuous Stream Active)<br>Active)</span>
                </div>
                <div class="mobile-input-row">
                    <div class="mobile-input-wrapper">
                        <input type="text" placeholder="Tap or speak command...">
                        <svg class="mobile-mic-svg" viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                        </svg>
                    </div>
                    <button class="mobile-send-button">Send</button>
                </div>
            `;
            
            container.appendChild(card);
        }
    }
});
</script>
'''

if '</body>' in code:
    code = code.replace('</body>', surgical_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Surgical clean mobile patch injected!")
else:
    print("ERROR: Body tag not found.")
