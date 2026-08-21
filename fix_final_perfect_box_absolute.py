with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean up previous injected boxes
code = re.sub(r'<style>[\s\S]*?/\* ABSOLUTE PERFECT BOX \*/[\s\S]*?</style>', '', code)
code = re.sub(r'<div id="pure-mobile-bottom-panel">[\s\S]*?</div>', '', code)
code = re.sub(r'<div id="perfect-mobile-box">[\s\S]*?</div>', '', code)

absolute_perfect_patch = '''
<style>
/* ABSOLUTE PERFECT BOX */
#perfect-mobile-box {
    display: none !important;
}

@media screen and (max-width: 768px) {
    /* Hide old raw input boxes on mobile to prevent clutter */
    form, .input-container {
        display: none !important;
    }

    #perfect-mobile-box {
        display: flex !important;
        flex-direction: column !important;
        background: rgba(0, 15, 20, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 14px !important;
        padding: 14px !important;
        margin: 12px 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.25) !important;
    }
}
</style>

<div id="perfect-mobile-box">
    <div style="text-align: center; color: #00ffcc; font-family: monospace; font-size: 11px; font-weight: bold; margin-bottom: 10px; letter-spacing: 0.5px; line-height: 1.3;">
        LISTENING...<br>
        <span style="font-weight: normal; opacity: 0.85; font-size: 90%;">(Continuous Stream Active)</span>
    </div>
    <div style="display: flex; gap: 8px; align-items: center; width: 100%; box-sizing: border-box;">
        <div style="flex: 1; height: 40px; background: rgba(0, 5, 10, 0.9); border: 1px solid rgba(0, 255, 204, 0.6); border-radius: 8px; display: flex; align-items: center; padding: 0 10px; box-sizing: border-box;">
            <input type="text" placeholder="Tap or speak command..." style="width: 100%; background: transparent; border: none; color: #00ffcc; font-family: monospace; font-size: 12px; outline: none;">
            <svg style="width: 16px; height: 16px; fill: #00ffcc; flex-shrink: 0; margin-left: 6px; cursor: pointer;" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
        </div>
        <button style="height: 40px; background: rgba(0, 136, 136, 0.95); border: 1px solid #00ffcc; border-radius: 8px; color: #ffffff; padding: 0 16px; font-family: monospace; font-size: 12px; font-weight: bold; cursor: pointer; flex-shrink: 0; box-shadow: 0 0 8px rgba(0, 255, 204, 0.35);">Send</button>
    </div>
</div>
'''

if '</body>' in code:
    code = code.replace('</body>', absolute_perfect_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Absolute perfect box patched!")
else:
    print("ERROR: Body tag not found.")
