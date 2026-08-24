with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

mobile_engine = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    body {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 100vh !important;
        padding: 10px !important;
        overflow-y: auto !important;
        background: #000 !important;
    }
    div, section, header, footer {
        position: relative !important;
        top: auto !important;
        left: auto !important;
        right: auto !important;
        bottom: auto !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 6px 0 !important;
        transform: none !important;
    }
    canvas {
        width: 100% !important;
        height: 280px !important;
        display: block !important;
        margin: 10px auto !important;
    }
}
</style>
'''

if '</head>' in code:
    code = code.replace('</head>', mobile_engine + '\n</head>')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Backend HTML string patched successfully!")
else:
    print("ERROR: Head tag not found in main.py string.")
