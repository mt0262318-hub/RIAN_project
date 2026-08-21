with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean any old injections
code = re.sub(r'<style>[\s\S]*?/\* NATIVE MOBILE ENHANCEMENT \*/[\s\S]*?</style>', '', code)

native_patch = '''
<style>
/* NATIVE MOBILE ENHANCEMENT */
@media screen and (max-width: 768px) {
    /* Target the app's native input container/form on mobile */
    form, .input-container, div:has(input[type="text"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        background: rgba(0, 15, 20, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 14px !important;
        padding: 12px !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.3) !important;
        width: 100% !important;
        margin: 10px 0 !important;
    }

    /* Make input text field stretch cleanly */
    input[type="text"] {
        flex: 1 1 auto !important;
        min-width: 0 !important;
        background: transparent !important;
        border: none !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        font-size: 12px !important;
        outline: none !important;
    }

    /* Make Send button locked and clean */
    button {
        flex: 0 0 auto !important;
        background: rgba(0, 136, 136, 0.95) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 9px !important;
        color: #ffffff !important;
        padding: 0 16px !important;
        font-family: monospace !important;
        font-size: 12px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.35) !important;
        white-space: nowrap !important;
    }
}
</style>
'''

if '</head>' in code:
    code = code.replace('</head>', native_patch + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Native mobile box enhancement applied!")
else:
    print("ERROR: Head tag not found.")
