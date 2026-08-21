with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Clean up previous scripts
code = re.sub(r'<script>[\s\S]*?Working matrix patched[\s\S]*?</script>', '', code)
code = re.sub(r'<script>[\s\S]*?Pro Matrix Injector[\s\S]*?</script>', '', code)

final_working_patch = '''
<style>
@media screen and (max-width: 768px) {
    /* Style mobile input containers to match the gorgeous glass card perfectly */
    form, .input-container, div[class*="input"] {
        background: rgba(0, 15, 20, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 14px !important;
        padding: 14px !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.3) !important;
        margin: 10px 0 !important;
        width: 100% !important;
    }
}
</style>

<script>
window.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        // Find existing input elements on mobile and enhance them gracefully without breaking functionality
        setTimeout(() => {
            const inputs = document.querySelectorAll('input[type="text"]');
            inputs.forEach(inp => {
                if (!inp.dataset.enhanced) {
                    inp.dataset.enhanced = "true";
                    inp.style.background = "transparent";
                    inp.style.border = "none";
                    inp.style.color = "#00ffcc";
                    inp.style.fontFamily = "monospace";
                    inp.style.outline = "none";
                    inp.placeholder = "Tap or speak command...";
                }
            });
        }, 500);
    }
});
</script>
'''

if '</body>' in code:
    code = code.replace('</body>', final_working_patch + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Exact bottom box mobile enhancement patched!")
else:
    print("ERROR: Body tag not found.")
