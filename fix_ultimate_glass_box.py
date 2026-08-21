with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean up previous injections
code = re.sub(r'<style>[\s\S]*?/\* ULTIMATE GLASS BOX \*/[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?Ultimate Mobile Injector[\s\S]*?</script>', '', code)

ultimate_patch = '''
<style>
/* ULTIMATE GLASS BOX */
@media screen and (max-width: 768px) {
    /* Target container safety */
    body {
        background: #000 !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    /* Absolute locked styling for the injected mobile box to prevent any button overflow */
    #ultimate-mobile-glass-card {
        display: flex !important;
        flex-direction: column !important;
        background: rgba(0, 15, 20, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 14px !important;
        padding: 14px !important;
        margin: 15px auto !important;
        width: calc(100% - 20px) !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.3) !important;
        position: relative !important;
        z-index: 99999 !important;
    }

    .u-input-row {
        display: flex !important;
        gap: 8px !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .u-input-wrapper {
        flex: 1 !important;
        min-width: 0 !important;
        height: 42px !important;
        background: rgba(0, 5, 10, 0.9) !important;
        border: 1px solid rgba(0, 255, 204, 0.6) !important;
        border-radius: 9px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 10px !important;
        box-sizing: border-box !important;
    }

    .u-input-wrapper input {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        font-size: 12px !important;
        outline: none !important;
        box-sizing: border-box !important;
    }

    .u-send-btn {
        height: 42px !important;
        background: rgba(0, 136, 136, 0.95) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 9px !important;
        color: #ffffff !important;
        padding: 0 16px !important;
        font-family: monospace !important;
        font-size: 12px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.35) !important;
        box-sizing: border-box !important;
    }
}
/* Hidden on Desktop */
#ultimate-mobile-glass-card {
    display: none;
}
</style>

<script>
/* Ultimate Mobile Injector */
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        if (!document.getElementById('ultimate-mobile-glass-card')) {
            const card = document.createElement('div');
            card.id = 'ultimate-mobile-glass-card';
            card.innerHTML = `
                <div style="text-align: center; color: #00ffcc; font-family: monospace; font-size: 11px; font-weight: bold; margin-bottom: 10px; letter-spacing: 0.5px; line-height: 1.3;">
                    LISTENING...<br>
                    <span style="font-weight: normal; opacity: 0.85; font-size: 90%;">(Continuous Stream Active)</span>
                </div>
                <div class="u-input-row">
                    <div class="u-input-wrapper">
                        <input type="text" placeholder="Tap or speak command...">
                        <svg style="width: 16px; height: 16px; fill: #00ffcc; flex-shrink: 0; margin-left: 6px; cursor: pointer;" viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                        </svg>
                    </div>
                    <button class="u-send-btn">Send</button>
                </div>
            `;
            document.body.appendChild(card);
        }
    }
});
</script>
'''

if '</body>' in code:
    code = code.replace('</body>', ultimate_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Ultimate glass box patched successfully!")
else:
    print("ERROR: Body tag not found.")
