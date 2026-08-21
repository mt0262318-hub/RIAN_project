with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean up previous injection
code = re.sub(r'<script>[\s\S]*?Pro Matrix Injector[\s\S]*?</script>', '', code)

working_patch = '''
<script>
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        // Remove old if exists
        const oldBox = document.getElementById('pro-mobile-matrix-box');
        if (oldBox) oldBox.remove();

        // Hide old cluttered inputs
        document.querySelectorAll('form, .input-container').forEach(el => {
            el.style.display = 'none';
        });

        const proBox = document.createElement('div');
        proBox.id = 'pro-mobile-matrix-box';
        proBox.style.cssText = 'position: relative; z-index: 999999; display: flex; flex-direction: column; background: rgba(0, 15, 20, 0.9); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid #00ffcc; border-radius: 14px; padding: 14px; margin: 15px auto; width: calc(100% - 20px); max-width: 450px; box-sizing: border-box; box-shadow: 0 0 20px rgba(0, 255, 204, 0.3);';

        proBox.innerHTML = `
            <div style="text-align: center; color: #00ffcc; font-family: monospace; font-size: 11px; font-weight: bold; margin-bottom: 10px; letter-spacing: 0.5px; line-height: 1.3;">
                LISTENING...<br>
                <span style="font-weight: normal; opacity: 0.85; font-size: 90%;">(Continuous Stream Active)</span>
            </div>
            
            <div style="display: flex; flex-direction: row; flex-wrap: nowrap; gap: 8px; align-items: center; width: 100%; box-sizing: border-box;">
                
                <!-- Explicit Input Box with Visible Field and Mic Icon -->
                <div style="flex: 1 1 auto; min-width: 0; height: 42px; background: rgba(0, 5, 10, 0.95); border: 1px solid rgba(0, 255, 204, 0.7); border-radius: 9px; display: flex; align-items: center; padding: 0 10px; box-sizing: border-box;">
                    <input type="text" placeholder="Tap or speak command..." style="flex: 1 1 auto; min-width: 0; width: 100%; background: transparent; border: none; color: #00ffcc; font-family: monospace; font-size: 12px; outline: none; box-sizing: border-box; display: block !important; visibility: visible !important;">
                    
                    <svg style="flex: 0 0 16px; width: 16px; height: 16px; fill: #00ffcc; margin-left: 6px; cursor: pointer; display: block !important;" viewBox="0 0 24 24">
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                    </svg>
                </div>
                
                <button style="flex: 0 0 auto; height: 42px; background: rgba(0, 136, 136, 0.95); border: 1px solid #00ffcc; border-radius: 9px; color: #ffffff; padding: 0 16px; font-family: monospace; font-size: 12px; font-weight: bold; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 204, 0.35); box-sizing: border-box; white-space: nowrap;">Send</button>
            
            </div>
        `;
        
        document.body.appendChild(proBox);
    }
});
</script>
'''

if '</body>' in code:
    code = code.replace('</body>', working_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Working matrix patched!")
else:
    print("ERROR: Body tag not found.")
