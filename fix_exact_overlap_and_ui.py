with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean up previous mobile template injections
code = re.sub(r'<style>[\s\S]*?#mobile-exact-app[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?mobile-exact-app[\s\S]*?</script>', '', code)

# Strict Non-Overlapping Mobile UI CSS & JS
strict_ui_patch = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    body {
        background: #000 !important;
        margin: 0 !important;
        padding: 10px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Strict Mobile App Container to prevent any overlap */
    #strict-mobile-shell {
        width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        box-sizing: border-box !important;
    }

    /* Bottom Listening & Input Panel matching Reference Image 101% */
    .strict-bottom-card {
        background: rgba(0, 15, 20, 0.75) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(0, 255, 204, 0.7) !important;
        border-radius: 14px !important;
        padding: 12px 14px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.15) !important;
    }

    .strict-listening-text {
        font-family: monospace !important;
        font-size: 11px !important;
        color: #00ffcc !important;
        text-align: center !important;
        line-height: 1.3 !important;
        font-weight: bold !important;
        letter-spacing: 0.5px !important;
    }

    .strict-input-row {
        display: flex !important;
        gap: 8px !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .strict-input-box {
        flex: 1 !important;
        height: 40px !important;
        background: rgba(0, 5, 10, 0.8) !important;
        border: 1px solid rgba(0, 255, 204, 0.6) !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 10px !important;
        box-sizing: border-box !important;
    }

    .strict-input-box input {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        font-size: 12px !important;
        outline: none !important;
    }

    .strict-input-box input::placeholder {
        color: rgba(0, 255, 204, 0.4) !important;
    }

    .strict-mic-icon {
        width: 16px !important;
        height: 16px !important;
        fill: #00ffcc !important;
        flex-shrink: 0 !important;
        margin-left: 6px !important;
        cursor: pointer !important;
    }

    .strict-send-btn {
        height: 40px !important;
        background: rgba(0, 136, 136, 0.9) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 0 16px !important;
        font-family: monospace !important;
        font-size: 12px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.3) !important;
    }
}
</style>

<script>
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        // Create strict non-overlapping wrapper if not exists
        if (!document.getElementById('strict-mobile-shell')) {
            const shell = document.createElement('div');
            shell.id = 'strict-mobile-shell';

            // Find existing components
            const canvas = document.getElementById('canvas3d') || document.querySelector('canvas');
            const logs = document.querySelector('.desktop-layout') || document.querySelector('.hud-glass');

            if (canvas && logs && canvas.parentElement) {
                const parent = canvas.parentElement;
                
                // Build exact bottom card matching target mockup
                const bottomCard = document.createElement('div');
                bottomCard.className = 'strict-bottom-card';
                bottomCard.innerHTML = `
                    <div class="strict-listening-text">
                        LISTENING...<br>
                        <span style="font-size: 95%; font-weight: normal; opacity: 0.85;">(Continuous Stream Active)<br>Active)</span>
                    </div>
                    <div class="strict-input-row">
                        <div class="strict-input-box">
                            <input type="text" placeholder="Tap or speak command...">
                            <svg class="strict-mic-icon" viewBox="0 0 24 24">
                                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                            </svg>
                        </div>
                        <button class="strict-send-btn">Send</button>
                    </div>
                `;

                // Append cleanly without overlapping
                parent.appendChild(bottomCard);
            }
        }
    }
});
</script>
'''

if '</body>' in code:
    code = code.replace('</body>', strict_ui_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Strict non-overlapping UI patch injected!")
else:
    print("ERROR: Body tag not found.")
