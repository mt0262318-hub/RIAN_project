with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up previous mobile style/script blocks
import re
code = re.sub(r'<style>[\s\S]*?/\* DOM REORDER SCOPE \*/[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?Mobile DOM Restructuring[\s\S]*?</script>', '', code)

# Professional Mobile DOM Restructuring & CSS
dom_reorder_patch = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* DOM REORDER SCOPE - DESKTOP 100% UNTOUCHED */
@media screen and (max-width: 768px) {
    body {
        background: #000 !important;
        margin: 0 !important;
        padding: 10px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    /* Fixed styling for log containers on mobile */
    .desktop-layout, .hud-glass, .log-stream, [class*="desktop-logs"] {
        width: 100% !important;
        max-height: 190px !important;
        overflow-y: scroll !important;
        overflow-x: hidden !important;
        margin: 6px 0 !important;
        box-sizing: border-box !important;
    }

    /* Canvas styling in center */
    #canvas3d {
        width: 100% !important;
        height: 240px !important;
        display: block !important;
        margin: 10px auto !important;
    }

    /* Input controls at bottom */
    form, input, textarea, button, .input-container {
        width: 100% !important;
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

<script>
/* Mobile DOM Restructuring Engine */
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        const canvas = document.getElementById('canvas3d');
        const logs = document.querySelector('.desktop-layout') || document.querySelector('.hud-glass');
        const container = canvas ? canvas.parentElement : null;
        
        if (canvas && logs && container) {
            // Physically reposition canvas to be right between logs and input controls
            // Target mockup: Header/Status -> Logs -> Canvas (Center) -> Input/Send
            container.insertBefore(canvas, logs.nextSibling);
        }
    }
});
</script>
'''

if '</head>' in code:
    code = code.replace('</head>', dom_reorder_patch + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: DOM reordering patch injected successfully!")
else:
    print("ERROR: Head tag not found.")
