with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up previous mobile style blocks
import re
code = re.sub(r'<style>[\s\S]*?/\* PRECISION MOBILE SCOPE \*/[\s\S]*?</style>', '', code)

# Precision Mobile CSS using Exact IDs and Classes found from inspection
precision_mobile_css = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* PRECISION MOBILE SCOPE - ZERO DESKTOP IMPACT */
@media screen and (max-width: 768px) {
    /* Mobile Body Setup */
    body {
        background: #000 !important;
        margin: 0 !important;
        padding: 8px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Target specific components using exact inspection names */
    
    /* 1. Status & Logs at the TOP */
    .desktop-layout, .hud-glass, .log-stream, [class*="desktop-logs"] {
        order: 1 !important;
        width: 100% !important;
        max-height: 180px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        position: relative !important;
        margin: 4px 0 !important;
    }

    /* 2. 3D Sphere Canvas in the EXACT CENTER */
    #canvas3d {
        order: 2 !important;
        width: 100% !important;
        height: 240px !important;
        display: block !important;
        margin: 10px auto !important;
        position: relative !important;
    }

    /* 3. Input & Send controls at the BOTTOM */
    form, input, textarea, button, .input-container {
        order: 3 !important;
        width: 100% !important;
        position: relative !important;
        margin-top: 8px !important;
        box-sizing: border-box !important;
    }

    /* Glowing Sidebar Scrollbar ("dandi") */
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
    code = code.replace('</head>', precision_mobile_css + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Precision mobile layout injected successfully!")
else:
    print("ERROR: Head tag not found.")
