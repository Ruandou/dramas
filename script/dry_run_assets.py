#!/usr/bin/env python3
"""Dry-run: audit remaining image assets needed for 满级影后她装新人"""
import json, os, re

BASE = 'dramas/满级影后她装新人'

# Load existing assets
with open(f'{BASE}/assets/looks/cdn_urls.json') as f:
    looks = json.load(f)
with open(f'{BASE}/assets/scenes/cdn_urls.json') as f:
    scenes = json.load(f)

# === GROUP CHARACTERS ===
group_chars = {
    'CHAR-GRP-02': '考核评委', 'CHAR-GRP-03': '陆景深助理',
    'CHAR-GRP-04': '方芷晴助理', 'CHAR-GRP-05': '周瑶父亲(电话)',
    'CHAR-GRP-06': '安保人员', 'CHAR-GRP-07': '老戏骨评委',
    'CHAR-GRP-08': '幕后大佬代理人', 'CHAR-GRP-09': '记者群',
    'CHAR-GRP-10': '组委会主席', 'CHAR-GRP-11': '年轻演员',
    'CHAR-GRP-12': '电影导演', 'CHAR-GRP-15': '综艺导演组',
    'CHAR-GRP-16': '颁奖嘉宾', 'CHAR-GRP-18': '片场导演',
    'CHAR-GRP-19': '星耀工作人员', 'CHAR-GRP-20': '练习生A',
    'CHAR-GRP-21': '练习生B', 'CHAR-GRP-22': '肖铭远助理',
}

existing_grp = [k for k in looks if k.startswith('CHAR-GRP')]
print(f"Existing group looks: {existing_grp}")

missing_grp = {k: v for k, v in group_chars.items() if f'{k}-L01' not in looks}
print(f"\nMissing group characters ({len(missing_grp)}):")
for k, v in sorted(missing_grp.items()):
    print(f"  {k} - {v}")

# === NEW SCENES ===
existing_scenes = set(scenes.keys())
all_scene_refs = set()
for ep in range(1, 73):
    ep_dir = f'{BASE}/剧本/EP{ep:02d}'
    for fn in os.listdir(ep_dir):
        if fn.endswith('.md') or fn.endswith('.yaml'):
            with open(f'{ep_dir}/{fn}') as f:
                all_scene_refs.update(re.findall(r'SCENE-0(\d+)', f.read()))

existing_scenes = set(scenes.keys())
referenced = {f'SCENE-{int(s):03d}' for s in all_scene_refs}
new_scenes = referenced - existing_scenes
print(f"\nNew scenes referenced but no TOS URL ({len(new_scenes)}):")
for s in sorted(new_scenes):
    print(f"  {s}")

# === CROSS-REF: which episodes use each missing asset ===
print(f"\n=== IMPACT ANALYSIS ===")
for s in sorted(new_scenes):
    episodes = []
    for ep in range(1, 73):
        for fn in os.listdir(f'{BASE}/剧本/EP{ep:02d}'):
            if fn.endswith('.yaml'):
                with open(f'{BASE}/剧本/EP{ep:02d}/{fn}') as f:
                    if s in f.read():
                        episodes.append(f'EP{ep:02d}')
    print(f"  {s}: used in {', '.join(sorted(set(episodes))[:5])}...")

for k in sorted(missing_grp):
    episodes = []
    for ep in range(1, 73):
        for fn in os.listdir(f'{BASE}/剧本/EP{ep:02d}'):
            if fn.endswith('.yaml'):
                with open(f'{BASE}/剧本/EP{ep:02d}/{fn}') as f:
                    if k in f.read():
                        episodes.append(f'EP{ep:02d}')
    print(f"  {k}: used in {len(episodes)} episodes ({', '.join(sorted(set(episodes))[:3])}...)")

print(f"\n=== SUMMARY ===")
print(f"Group L01 images needed: {len(missing_grp)}")
print(f"New scene images needed: {len(new_scenes)}")
print(f"Total: {len(missing_grp) + len(new_scenes)} images")
print(f"Model: doubao-seedream-5-0-lite-260128")
print(f"NOTE: All generation incurs API costs (方舟扣费)")
print(f"NOTE: Group char prompts need descriptions from 角色卡片.md + 声音卡片.md")
