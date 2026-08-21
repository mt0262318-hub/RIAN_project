with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up any prior broken injection blocks
import re
code = re.sub(r'<style>[\s\S]*?/\* STRICT PRO MOBILE SCOPE \*/[\s\S]*?</style>', '', code)

# Bulletproof Isolated Mobile CSS & Layout Scoping
pro_isolated_css = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* STRICT PRO MOBILE SCOPE - GUARANTEES ZERO IMPACT ON DESKTOP */
@media screen and (max-width: 768px) {
    /* Base mobile body setup */
    body {
        background: #000 !important;
        margin: 0 !important;
        padding: 8px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    /* Force mobile container to stack vertically in exact target order */
    body, html {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Target specific components safely without global leaks */
    canvas {
        order: 2 !important;
        width: 100% !important;
        height: 240px !important;
        display: block !important;
        margin: 10px auto !important;
    }

    /* Log and status panels at top */
    [class*="log"], [class*="test"], [class*="runner"], pre, code, [class*="status"] {
        order: 1 !important;
        max-height: 170px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        border: 1px solid #00ffcc !important;
        background: rgba(0, 15, 15, 0.95) !important;
        box-sizing: border-box !important;
    }

    /* Input and send controls at bottom */
    .input-container, form, input[type="text"], textarea, button, [class*="input"], [class*="send"] {
        order: 3 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin-top: 10px !important;
    }

    /* Custom glowing scrollbar ("dandi") */
    ::-webkit-scrollbar {
        width: 5px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #00ffcc !important;
        border-radius: 3px !important;
    }
    ::-webkit-scrollbar-track {
        background: #001111 !important;
    }
}
</style>
'''

if '</head>' in code:
    code = code.replace('</head>', pro_isolated_css + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Pro isolated mobile layout successfully injected!")
else:
    print("ERROR: Head tag not found.")
