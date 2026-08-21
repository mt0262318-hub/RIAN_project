import os
import re

index_files = []
for root, dirs, files in os.walk('.'):
    if 'index.html' in files:
        index_files.append(os.path.join(root, 'index.html'))

print(f"Found index files at: {index_files}")

mobile_fix = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@media screen and (max-width: 768px) {
    body {
        width: 100vw !important;
        height: 100vh !important;
        overflow: auto !important;
        background: #000 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    .container, #app, canvas {
        max-width: 100% !important;
        height: auto !important;
        transform: scale(0.9) !important;
        transform-origin: top center !important;
    }
}
</style>
"""

for path in index_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'<meta[^>]*name=["\']viewport["\'][^>]*>', '', content, flags=re.IGNORECASE)
    
    if '</head>' in content:
        content = content.replace('</head>', mobile_fix + '\n</head>')
    else:
        content = mobile_fix + content
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"SUCCESS: Mobile responsive fix injected into {path}")
