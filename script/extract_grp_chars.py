#!/usr/bin/env python3
"""Extract group character visual descriptions from character card."""
with open('dramas/满级影后她装新人/资产/角色卡片.md') as f:
    content = f.read()

# Find all group character sections
import re
sections = re.split(r'(?=### CHAR-GRP-\d+)', content)
for s in sections:
    if 'CHAR-GRP-' not in s:
        continue
    grp_match = re.search(r'(CHAR-GRP-\d+)', s)
    name_match = re.search(r'\n([^\n]+)\n', s[s.find('| **姓名**'):]) if '| **姓名**' in s else None
    appearance_match = re.search(r'\*\*外貌关键词\*\*：([^\n]+)', s)
    desc_match = re.search(r'\*\*角色描述\*\*：([^\n]+)', s)
    
    grp_id = grp_match.group(1) if grp_match else '?'
    
    # Extract key visual info
    print(f'\n=== {grp_id} ===')
    
    # Get name
    for line in s.split('\n'):
        if '**姓名**' in line:
            name = line.split('|')[2].strip() if '|' in line else line
            print(f'  Name: {name}')
    
    if appearance_match:
        print(f'  Appearance: {appearance_match.group(1)[:100]}')
    if desc_match:
        print(f'  Description: {desc_match.group(1)[:100]}')
    
    # Print all content
    for line in s.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('-'):
            if '|' in stripped:
                cols = [c.strip() for c in stripped.split('|')]
                if len(cols) == 3 and cols[0]:
                    key = cols[0].strip('* ')
                    val = cols[1] if len(cols) > 1 else ''
                    if key in ['姓名', '年龄', '外貌关键词', '首次登场', '对白性格', '语言风格']:
                        print(f'  {key}: {val[:100]}')
