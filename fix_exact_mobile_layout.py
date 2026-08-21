with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Exact Mobile Layout & Fixed Scrollbar CSS
exact_mobile_css = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    /* Enable Flex container on body for mobile re-ordering */
    body {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 100vh !important;
        padding: 10px !important;
        overflow-x: hidden !important;
        background: #000 !important;
        box-sizing: border-box !important;
    }

    /* Reset default absolute positioning for mobile stack */
    body > *, div, section, header, footer {
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

    /* SPECIFIC ORDER FOR MOBILE (Matching Reference Image) */
    /* 1. Header / Title at top */
    header, .header, h1, .title {
        order: 1 !important;
        text-align: center !important;
    }

    /* 2. Input / Command Box right below header */
    .input-container, form, input[type="text"], textarea, button, .chat-box {
        order: 2 !important;
    }

    /* 3. 3D Sphere Canvas in middle */
    canvas {
        order: 3 !important;
        width: 100% !important;
        height: 240px !important;
        display: block !important;
        margin: 10px auto !important;
    }

    /* 4. Autonomous Testing Log Box at bottom with FIXED height and custom scrollbar ("dandi") */
    pre, code, .log-box, .terminal-box, [class*="log"], [class*="test"], [class*="runner"], div:has(> pre) {
        order: 4 !important;
        height: 200px !important;
        max-height: 200px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        word-break: break-all !important;
        white-space: pre-wrap !important;
        border: 1px solid #00ffcc !important;
        background: rgba(0, 20, 20, 0.8) !important;
    }

    /* Custom glowing scrollbar (sidebar 'dandi') for log container */
    ::-webkit-scrollbar {
        width: 6px !important;
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
    code = code.replace('</head>', exact_mobile_css + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Exact mobile layout and scrollbar engine injected!")
else:
    print("ERROR: Head tag not found.")
