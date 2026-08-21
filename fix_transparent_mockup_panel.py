with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Precise Transparent Mockup CSS for Bottom Panel
transparent_panel_css = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    /* 100% Transparent Glassmorphism Container matching Reference Image */
    #mobile-exact-app .m-input-area {
        background: rgba(0, 10, 15, 0.45) !important;
        backdrop-filter: blur(6px) !important;
        -webkit-backdrop-filter: blur(6px) !important;
        border: 1px solid rgba(0, 255, 204, 0.6) !important;
        border-radius: 14px !important;
        padding: 14px !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15) inset, 0 0 10px rgba(0, 255, 204, 0.2) !important;
    }

    /* Status text styling */
    #mobile-exact-app .m-input-area > div:first-child {
        font-family: monospace !important;
        font-size: 11px !important;
        color: #00ffcc !important;
        text-align: center !important;
        margin-bottom: 8px !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 0 5px rgba(0,255,204,0.5) !important;
    }

    .m-input-row {
        display: flex !important;
        gap: 10px !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* Input wrapper matching mockup glass border */
    .m-input-field-wrapper {
        flex: 1 !important;
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        background: rgba(0, 5, 8, 0.6) !important;
        border: 1px solid rgba(0, 255, 204, 0.7) !important;
        border-radius: 10px !important;
        padding: 0 12px !important;
        height: 42px !important;
    }

    .m-input-field-wrapper input {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: #00ffcc !important;
        padding: 0 !important;
        font-family: monospace !important;
        font-size: 12px !important;
        outline: none !important;
    }

    .m-input-field-wrapper input::placeholder {
        color: rgba(0, 255, 204, 0.45) !important;
    }

    /* Mic icon inside wrapper */
    .m-mic-icon {
        width: 18px !important;
        height: 18px !important;
        fill: #00ffcc !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        margin-left: 8px !important;
        filter: drop-shadow(0 0 3px rgba(0,255,204,0.6)) !important;
    }

    /* Send button matching mockup cyan rounded look */
    .m-input-row button {
        background: rgba(0, 136, 136, 0.85) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 0 18px !important;
        height: 42px !important;
        font-weight: bold !important;
        font-family: monospace !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        box-shadow: 0 0 10px rgba(0, 255, 204, 0.3) !important;
        text-shadow: 0 0 3px rgba(0,255,204,0.5) !important;
    }
}
</style>
'''

if '</body>' in code:
    # Replace old bottom panel injection or append
    import re
    code = re.sub(r'<style>[\s\S]*?#mobile-exact-app \.m-input-area[\s\S]*?</style>', '', code)
    code = code.replace('</body>', transparent_panel_css + '\n</body>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Transparent mockup panel styles injected!")
else:
    print("ERROR: Body tag not found.")
