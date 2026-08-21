with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up previous heavy CSS hacks
if '<style>' in code:
    import re
    code = re.sub(r'<style>[\s\S]*?@media screen and \(max-width: 768px\)[\s\S]*?</style>', '', code)

# Professional Intelligent Mobile App Router & Layout Engine
true_mobile_engine = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
/* PC / Laptop view remains 100% untouched */
@media screen and (max-width: 768px) {
    body {
        background: #000 !important;
        color: #00ffcc !important;
        font-family: monospace !important;
        margin: 0 !important;
        padding: 12px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Hide desktop clutter wrappers if any, keep content flow */
    .desktop-only { display: none !important; }

    /* Mobile App Shell Styling matching Reference Image */
    #mobile-app-shell {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
    }

    /* 1. Status / Log Panel at Top */
    .mobile-top-panel {
        background: rgba(0, 20, 20, 0.8) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 8px !important;
        padding: 10px !important;
        max-height: 180px !important;
        overflow-y: scroll !important;
    }

    /* 2. 3D Canvas in Center */
    canvas {
        width: 100% !important;
        height: 240px !important;
        display: block !important;
        margin: 0 auto !important;
    }

    /* 3. Bottom Input & Voice Command Section */
    .mobile-bottom-panel {
        background: rgba(0, 15, 15, 0.9) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 8px !important;
        padding: 12px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
    }
}
</style>

<script>
/* Intelligent Mobile DOM Restructuring Engine */
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        // Find key elements in the existing dashboard
        const canvas = document.querySelector('canvas');
        const logs = document.querySelector('pre') || document.querySelector('[class*="log"]') || document.querySelector('code');
        const inputs = document.querySelector('form') || document.querySelector('.input-container') || document.querySelector('input');
        
        if (canvas && logs && inputs) {
            // Create a dedicated mobile app container if not exists
            let shell = document.getElementById('mobile-app-shell');
            if (!shell) {
                shell = document.createElement('div');
                shell.id = 'mobile-app-shell';
                
                // Top section for logs/status
                const topDiv = document.createElement('div');
                topDiv.className = 'mobile-top-panel';
                topDiv.appendChild(logs.cloneNode(true));
                
                // Bottom section for input/controls
                const bottomDiv = document.createElement('div');
                bottomDiv.className = 'mobile-bottom-panel';
                bottomDiv.appendChild(inputs.cloneNode(true));
                
                // Append in exact target order: Top -> Canvas -> Bottom
                document.body.innerHTML = '';
                document.body.appendChild(topDiv);
                document.body.appendChild(canvas);
                document.body.appendChild(bottomDiv);
            }
        }
    }
});
</script>
'''

if '</head>' in code:
    code = code.replace('</head>', true_mobile_engine + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Intelligent mobile app router injected!")
else:
    print("ERROR: Head tag not found.")
