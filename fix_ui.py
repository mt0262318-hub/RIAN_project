import re

with open('./ui/index.html', 'r') as f:
    content = f.read()

# 1. Purane sabhi viewport meta tags hataein
content = re.sub(r'<meta[^>]*name=["\']viewport["\'][^>]*>', '', content, flags=re.IGNORECASE)

# 2. Naya desktop mirror block head ke sabse upar daalein
desktop_mirror_block = '''<head>
<meta name="viewport" content="width=1200, initial-scale=0.33, maximum-scale=3.0, user-scalable=yes">
<style>
/* Absolute Desktop Mirror for Mobile */
body {
    width: 1200px !important;
    transform-origin: top left;
    transform: scale(0.35);
    overflow-x: auto !important;
    overflow-y: auto !important;
    background-color: #000 !important;
}
</style>'''

if '<head>' in content:
    content = content.replace('<head>', desktop_mirror_block, 1)
else:
    content = desktop_mirror_block + content

with open('./ui/index.html', 'w') as f:
    f.write(content)

print('SUCCESS: Desktop mirror successfully injected without errors!')
