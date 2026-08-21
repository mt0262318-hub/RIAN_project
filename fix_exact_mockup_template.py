with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up previous mobile injections
import re
code = re.sub(r'<style>[\s\S]*?/\* EXACT MOCKUP SCOPE \*/[\s\S]*?</style>', '', code)
code = re.sub(r'<script>[\s\S]*?Mobile DOM Restructuring[\s\S]*?</script>', '', code)

# Professional Mobile-Only Template Injector via JS
mobile_template_injector = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* DESKTOP STYLES UNTOUCHED */
@media screen and (max-width: 768px) {
    /* Hide messy desktop absolute elements on mobile */
    body > *:not(#mobile-exact-app) {
        display: none !important;
    }
    
    body {
        background: #000 !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        margin: 0 !important;
        padding: 12px !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
    }

    #mobile-exact-app {
        display: flex !important;
        flex-direction: column !important;
        gap: 14px !important;
        width: 100% !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }

    .m-box {
        background: rgba(0, 20, 25, 0.85) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 10px !important;
        padding: 12px !important;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.2) !important;
    }

    .m-logs {
        max-height: 190px !important;
        overflow-y: scroll !important;
        font-size: 11px !important;
        line-height: 1.4 !important;
    }

    .m-canvas-container {
        width: 100% !important;
        height: 240px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background: rgba(0, 5, 10, 0.5) !important;
        border-radius: 10px !important;
        border: 1px solid #00ffcc44 !important;
    }

    .m-canvas-container canvas {
        width: 100% !important;
        height: 100% !important;
        display: block !important;
    }

    .m-input-area {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
    }

    .m-input-row {
        display: flex !important;
        gap: 8px !important;
        align-items: center !important;
    }

    .m-input-row input {
        flex: 1 !important;
        background: rgba(0, 10, 15, 0.9) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 6px !important;
        color: #00ffcc !important;
        padding: 10px !important;
        font-family: monospace !important;
    }

    .m-input-row button {
        background: #008888 !important;
        border: 1px solid #00ffcc !important;
        border-radius: 6px !important;
        color: #fff !important;
        padding: 10px 16px !important;
        font-weight: bold !important;
        cursor: pointer !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px !important; }
    ::-webkit-scrollbar-thumb { background: #00ffcc !important; border-radius: 3px !important; }
}
</style>

<script>
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        // Create exact mockup app structure
        if (!document.getElementById('mobile-exact-app')) {
            const app = document.createElement('div');
            app.id = 'mobile-exact-app';

            // 1. Top Section: Status & Logs
            const topBox = document.createElement('div');
            topBox.className = 'm-box m-logs';
            const originalLogs = document.querySelector('.desktop-layout') || document.querySelector('.hud-glass') || document.querySelector('pre');
            topBox.innerHTML = '<strong>SYSTEM STATUS: ONLINE</strong><br><br>' + (originalLogs ? originalLogs.innerHTML : 'Loading telemetry logs...');
            app.appendChild(topBox);

            // 2. Center Section: 3D Sphere Canvas
            const canvasContainer = document.createElement('div');
            canvasContainer.className = 'm-canvas-container';
            const canvas = document.getElementById('canvas3d') || document.querySelector('canvas');
            if (canvas) {
                canvasContainer.appendChild(canvas);
            }
            app.appendChild(canvasContainer);

            // 3. Bottom Section: Listening & Input Box
            const bottomBox = document.createElement('div');
            bottomBox.className = 'm-box m-input-area';
            bottomBox.innerHTML = `
                <div style="font-size: 12px; color: #00ffcc; text-align: center; margin-bottom: 4px; font-weight: bold;">
                    LISTENING...<br><span style="font-size: 10px; color: #88ffcc;">(Continuous Stream Active)</span>
                </div>
                <div class="m-input-row">
                    <input type="text" placeholder="Tap or speak command..." id="m-cmd-input">
                    <button id="m-send-btn">Send</button>
                </div>
            `;
            app.appendChild(bottomBox);

            document.body.appendChild(app);
        }
    }
});
</script>
'''

if '</head>' in code:
    code = code.replace('</head>', mobile_template_injector + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Exact mobile mockup template injected!")
else:
    print("ERROR: Head tag not found.")
