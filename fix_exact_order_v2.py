with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Exact Third Image Layout Mapping for Mobile
perfect_mobile_css = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    /* Mobile Screen Container */
    body {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 100vh !important;
        padding: 8px !important;
        overflow-x: hidden !important;
        background: #000 !important;
        box-sizing: border-box !important;
    }

    /* Reset positioning */
    body > *, div, section, header, footer {
        position: relative !important;
        top: auto !important;
        left: auto !important;
        right: auto !important;
        bottom: auto !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 4px 0 !important;
        transform: none !important;
    }

    /* --- EXACT ORDER MATCHING 3RD IMAGE --- */
    
    /* 1. Status & Log boxes at the TOP */
    header, .header, h1, .title, 
    [class*="status"], [class*="system"], 
    [class*="log"], [class*="test"], [class*="runner"], pre, code {
        order: 1 !important;
    }

    /* Specific Log Box Height & Scrollbar ('dandi') */
    pre, code, .log-box, .terminal-box, [class*="log"], [class*="runner"] {
        max-height: 160px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        border: 1px solid #00ffcc !important;
        background: rgba(0, 15, 15, 0.9) !important;
    }

    /* 2. 3D Particle Sphere Canvas in the CENTER */
    canvas {
        order: 2 !important;
        width: 100% !important;
        height: 220px !important;
        display: block !important;
        margin: 8px auto !important;
    }

    /* 3. Input, Speak & Send Box at the BOTTOM */
    .input-container, form, input[type="text"], textarea, button, [class*="input"], [class*="send"], [class*="mic"] {
        order: 3 !important;
    }

    /* Custom glowing scrollbar */
    ::-webkit-scrollbar {
        width: 5px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #00ffcc !important;
        border-radius: 3px !important;
    }
}
</style>
'''

if '</head>' in code:
    code = code.replace('</head>', perfect_mobile_css + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Exact 3D-Center mobile layout injected!")
else:
    print("ERROR: Head tag not found.")
