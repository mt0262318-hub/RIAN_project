with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Professional Mobile Scroll & Layout Fix CSS
mobile_perfect_css = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    /* Mobile Container Flow */
    body {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 100vh !important;
        padding: 10px !important;
        overflow-y: auto !important;
        background: #000 !important;
        box-sizing: border-box !important;
    }
    
    /* Reset all absolute/fixed positioning for mobile stacking */
    div, section, header, footer {
        position: relative !important;
        top: auto !important;
        left: auto !important;
        right: auto !important;
        bottom: auto !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 6px 0 !important;
        transform: none !important;
    }

    /* FIX FOR LOG BOX: Internal scroll instead of expanding and pushing up */
    pre, code, .log-box, .terminal-box, [class*="log"], [class*="test"], [class*="runner"] {
        max-height: 180px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        word-break: break-all !important;
        white-space: pre-wrap !important;
    }

    /* 3D Canvas Sizing for Phone */
    canvas {
        width: 100% !important;
        height: 250px !important;
        display: block !important;
        margin: 10px auto !important;
    }

    /* Input Box fixed nicely at lower section */
    input, textarea, button, .input-container {
        width: 100% !important;
        box-sizing: border-box !important;
    }
}
</style>
'''

# Remove any previous injected mobile blocks to keep code clean
if '<style>' in code:
    import re
    code = re.sub(r'<meta name="viewport"[^>]*>', '', code)

if '</head>' in code:
    code = code.replace('</head>', mobile_perfect_css + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Perfect mobile scroll and layout engine injected into main.py!")
else:
    print("ERROR: Head tag not found in main.py")
