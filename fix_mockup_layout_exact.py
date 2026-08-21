with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up previous injected blocks
import re
code = re.sub(r'<style>[\s\S]*?/\* EXACT MOCKUP SCOPE \*/[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?Exact Mockup DOM Engine[\s\S]*?</script>', '', code)

# Professional Exact Mockup Layout CSS & JS
exact_mockup_patch = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* EXACT MOCKUP SCOPE - ZERO DESKTOP IMPACT */
@media screen and (max-width: 768px) {
    body {
        background: #000 !important;
        margin: 0 !important;
        padding: 10px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* 1. Status / Log Box at Top */
    .desktop-layout, .hud-glass, .log-stream, [class*="desktop-logs"] {
        order: 1 !important;
        width: 100% !important;
        max-height: 200px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        margin-bottom: 15px !important;
        box-sizing: border-box !important;
    }

    /* 2. 3D Sphere in Center */
    #canvas3d {
        order: 2 !important;
        width: 100% !important;
        height: 260px !important;
        display: block !important;
        margin: 15px auto !important;
    }

    /* 3. Input & Send Box at Bottom */
    form, input, textarea, button, .input-container {
        order: 3 !important;
        width: 100% !important;
        margin-top: 15px !important;
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
    code = code.replace('</head>', exact_mockup_patch + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Exact mockup layout injected successfully!")
else:
    print("ERROR: Head tag not found.")
