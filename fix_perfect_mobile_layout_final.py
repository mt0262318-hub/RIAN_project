with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean previous mobile injections cleanly
code = re.sub(r'<style>[\s\S]*?/\* PERFECT MOBILE LAYOUT \*/[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?Perfect Mobile Reorder[\s\S]*?</script>', '', code)
code = re.sub(r'<div id="perfect-mobile-box">[\s\S]*?</div>', '', code)

perfect_patch = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* PERFECT MOBILE LAYOUT - ZERO DESKTOP IMPACT */
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

    /* Main mobile app wrapper */
    #mobile-app-root {
        width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        box-sizing: border-box !important;
    }

    /* 1. Status / Logs at Top */
    .mobile-top-logs {
        order: 1 !important;
        width: 100% !important;
        max-height: 180px !important;
        overflow-y: scroll !important;
        background: rgba(0, 15, 20, 0.8) !important;
        border: 1px solid rgba(0, 255, 204, 0.7) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        box-sizing: border-box !important;
    }

    /* 2. 3D Sphere Canvas in Center */
    #canvas3d, canvas {
        order: 2 !important;
        width: 100% !important;
        height: 240px !important;
        display: block !important;
        margin: 0 auto !important;
    }

    /* 3. Perfect Glassmorphism Bottom Box at Bottom (No Overflow) */
    #perfect-mobile-box {
        order: 3 !important;
        display: flex !important;
        flex-direction: column !important;
        background: rgba(0, 15, 20, 0.75) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 12px !important;
        padding: 12px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.25) !important;
    }

    .m-input-row {
        display: flex !important;
        gap: 8px !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .m-input-field {
        flex: 1 !important;
        min-width: 0 !important;
        height: 40px !important;
        background: rgba(0, 5, 10, 0.85) !important;
        border: 1px solid rgba(0, 255, 204, 0.6) !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 10px !important;
        box-sizing: border-box !important;
    }

    .m-input-field input {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        font-size: 12px !important;
        outline: none !important;
    }

    .m-input-field input::placeholder {
        color: rgba(0, 255, 204, 0.4) !important;
    }

    .m-mic-btn {
        width: 16px !important;
        height: 16px !important;
        fill: #00ffcc !important;
        flex-shrink: 0 !important;
        margin-left: 6px !important;
        cursor: pointer !important;
    }

    .m-send-btn {
        height: 40px !important;
        background: rgba(0, 136, 136, 0.9) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 8px !important;
        color: #fff !important;
        padding: 0 14px !important;
        font-family: monospace !important;
        font-size: 12px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.3) !important;
    }
}

/* Hidden on desktop */
#perfect-mobile-box { display: none; }
</style>

<!-- Perfect Bottom Box HTML structure -->
<div id="perfect-mobile-box">
    <div style="text-align: center; color: #00ffcc; font-family: monospace; font-size: 11px; margin-bottom: 8px; font-weight: bold; letter-spacing: 0.5px;">
        LISTENING...<br>
        <span style="font-weight: normal; opacity: 0.85;">(Continuous Stream Active)</span>
    </div>
    <div class="m-input-row">
        <div class="m-input-field">
            <input type="text" placeholder="Tap or speak command...">
            <svg class="m-mic-btn" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
        </div>
        <button class="m-send-btn">Send</button>
    </div>
</div>
'''

if '</body>' in code:
    code = code.replace('</body>', perfect_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Perfect mobile layout patch applied!")
else:
    print("ERROR: Body tag not found.")
