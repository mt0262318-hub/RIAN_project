with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Only inject if not already injected to prevent bloat/crash
if '/* STABLE MOBILE BOX */' not in code:
    stable_patch = '''
<style>
/* STABLE MOBILE BOX */
@media screen and (max-width: 768px) {
    #mobile-bottom-box {
        display: flex !important;
        flex-direction: column !important;
        background: rgba(0, 15, 20, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid #00ffcc !important;
        border-radius: 14px !important;
        padding: 14px !important;
        margin: 15px auto !important;
        width: 90% !important;
        box-sizing: border-box !important;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.3) !important;
    }
}
#mobile-bottom-box { display: none; }
</style>

<div id="mobile-bottom-box">
    <div style="text-align: center; color: #00ffcc; font-family: monospace; font-size: 11px; margin-bottom: 8px;">LISTENING... (Continuous Stream Active)</div>
    <div style="display: flex; gap: 8px; align-items: center; width: 100%;">
        <input type="text" placeholder="Tap or speak..." style="flex: 1; background: rgba(0,5,10,0.9); border: 1px solid #00ffcc; border-radius: 8px; color: #00ffcc; padding: 10px; font-family: monospace; font-size: 12px; outline: none;">
        <button style="background: #008888; border: 1px solid #00ffcc; border-radius: 8px; color: #fff; padding: 10px 15px; font-weight: bold; cursor: pointer;">Send</button>
    </div>
</div>
'''
    # Safely insert before </head>
    new_code = code.replace('</head>', stable_patch + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("SUCCESS: Stable patch injected.")
else:
    print("Already injected.")
