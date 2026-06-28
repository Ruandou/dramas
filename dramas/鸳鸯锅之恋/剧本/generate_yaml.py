#!/usr/bin/env python3
"""Generate shots.yaml and segments.yaml for EP67-EP72 from .md script files."""
import re, os, json, textwrap

# CDN URLs for references
LOOKS_CDN = {
    "CHAR-001-L01": "CHAR-001-L01",
    "CHAR-002-L01": "CHAR-002-L01",
    "CHAR-003-L01": "CHAR-003-L01",
    "CHAR-004-L01": "CHAR-004-L01",
    "CHAR-005-L01": "CHAR-005-L01",
    "CHAR-006-L01": "CHAR-006-L01",
}
SCENE_CDN = {"SCENE-001": "SCENE-001", "SCENE-005": "SCENE-005"}
PROMPT_SUFFIX = "现代都市写实风格，暖色调，电影级质感，生活化场景。竖屏9比16。禁止画面中出现任何文字或字幕。"

# Character descriptions for images section
CHAR_DESC = {
    "CHAR-001-L01": "苏辣辣，27岁中国女性，心形脸大杏眼，齐肩微卷黑发低马尾，白T+修身牛仔裤+酒红围裙+辣椒项链",
    "CHAR-002-L01": "陆北辰，29岁中国男性，瘦长脸细长内双眼，银色细框眼镜，黑色短发，深蓝T+深灰牛仔裤+键盘帽吊坠",
    "CHAR-003-L01": "林小暖，26岁中国女性，圆润鹅蛋脸圆杏眼，半扎发+鲨鱼夹，藏蓝针织毛衣+浅色直筒牛仔裤+帆布鞋",
    "CHAR-004-L01": "赵大鹏，30岁中国男性，宽圆脸壮实身材，短圆寸头，红色Polo衫+卡其色短裤+运动鞋",
    "CHAR-005-L01": "苏爸，55岁中国男性，方圆脸丹凤眼，灰白短发，灰T+条纹围裙+深色长裤+黑布鞋",
    "CHAR-006-L01": "陆妈，56岁中国女性，圆脸烫卷栗色短发，深红V领针织开衫+白色高领+黑色直筒裤+皮鞋",
}
SCENE_DESC = {
    "SCENE-001": "苏记老火锅大堂，傍晚暖光灯笼照亮木质桌椅，墙上挂满老照片，红灯笼暖光",
    "SCENE-005": "苏辣辣家客厅，午后阳光从木窗格洒入暖黄光斑，藤椅茶几盖碗茶",
}

# Episodes to process
EPISODES = [
    {"ep": "EP67", "title": "满月宴", "file": "EP67/EP67_满月宴.md"},
    {"ep": "EP68", "title": "一周年", "file": "EP68/EP68_一周年.md"},
    {"ep": "EP69", "title": "传承", "file": "EP69/EP69_传承.md"},
    {"ep": "EP70", "title": "五年后", "file": "EP70/EP70_五年后.md"},
    {"ep": "EP71", "title": "故事回顾", "file": "EP71/EP71_故事回顾.md"},
    {"ep": "EP72", "title": "鸳鸯锅的结局", "file": "EP72/EP72_鸳鸯锅的结局.md"},
]

def parse_shots_from_md(filepath):
    """Extract shot data from the 11-column markdown table."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    shots = []
    current_seg = None
    seg_shots = {}
    
    # Find all segments and their shots
    lines = content.split('\n')
    in_table = False
    headers = []
    
    for i, line in enumerate(lines):
        # Detect segment headers
        seg_match = re.match(r'^## (SEG\d+) — (.+)', line)
        if seg_match:
            current_seg = seg_match.group(1)
            seg_shots[current_seg] = []
            continue
        
        # Detect table headers (11 columns)
        if '| 镜号 |' in line or '|shot_id|' in line.lower() or ('| 镜号' in line and 'shot_id' in line):
            in_table = True
            headers = [h.strip() for h in line.split('|') if h.strip()]
            continue
        
        # Skip separator lines
        if in_table and line.strip().startswith('|---'):
            continue
        
        # Parse table rows
        if in_table and line.strip().startswith('|') and current_seg:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) >= 10 and cells[0].isdigit():
                shot_num = int(cells[0])
                shot_id = cells[1].strip('`')
                scene = cells[2].strip('`')
                characters = [c.strip() for c in cells[3].split(',')]
                looks = [c.strip() for c in cells[4].split(',')]
                shot_size = cells[5]
                duration = int(cells[6])
                mode = cells[7].strip('`')
                camera = cells[8]
                description = cells[9]
                dialogue_raw = cells[10] if len(cells) > 10 else ''
                
                shot = {
                    'shot_num': shot_num,
                    'shot_id': shot_id,
                    'scene': scene,
                    'characters': characters,
                    'looks': looks,
                    'shot_size': shot_size,
                    'duration': duration,
                    'mode': mode,
                    'camera': camera,
                    'description': description,
                    'dialogue_raw': dialogue_raw,
                    'segment': current_seg,
                }
                shots.append(shot)
                if current_seg in seg_shots:
                    seg_shots[current_seg].append(shot)
            
            # End of table if empty line or new section
            if not line.strip().startswith('|'):
                in_table = False
    
    return shots, seg_shots

def parse_dialogue(dialogue_raw):
    """Parse dialogue string into structured format."""
    dialogues = []
    # Pattern: **CHAR-XXX**[emotion]：「text」 or **CHAR-XXX**[emotion·sub]：「text」
    # Also handle [待补：name]
    pattern = r'\*\*(.+?)\*\*\[(.+?)\]：「(.+?)」'
    matches = re.findall(pattern, dialogue_raw)
    for speaker_raw, emotion, line in matches:
        # Clean speaker
        speaker = speaker_raw.strip()
        if speaker.startswith('**'):
            speaker = speaker[2:]
        if speaker.endswith('**'):
            speaker = speaker[:-2]
        
        dialogues.append({
            'speaker': speaker,
            'emotion': emotion,
            'line': line,
        })
    
    # Also handle 旁白 pattern
    narr_pattern = r'\*\*旁白\*\*\[(.+?)\]：「(.+?)」'
    for emotion, line in re.findall(narr_pattern, dialogue_raw):
        dialogues.append({
            'speaker': '旁白',
            'emotion': emotion,
            'line': line,
        })
    
    return dialogues

def get_shot_size_code(size_name):
    """Convert Chinese shot size to code."""
    mapping = {
        '大特写': 'ECU', '特写': 'CU', '中特写': 'MCU',
        '中景': 'MS', '中全景': 'MLS', '全景': 'LS', '远景': 'ELS',
        '近景': 'MCU',
    }
    return mapping.get(size_name, 'MS')

def build_look_desc(look_id, char_list=None):
    """Get character description for images section."""
    # Handle [待补：xxx] entries
    if look_id.startswith('[待补：'):
        name = look_id.strip('[]')
        return f"{name}（待补群演，详见待补群演清单）"
    return CHAR_DESC.get(look_id, look_id)

def generate_shots_yaml(ep_data, shots):
    """Generate shots.yaml content."""
    ep = ep_data['ep']
    title = ep_data['title']
    total_dur = sum(s['duration'] for s in shots)
    
    lines = [
        f"# {ep} {title} — shots.yaml",
        f"# 从 {ep}_{title}.md 镜头表导出，勿手改 yaml 当源",
        f"# {len(shots)} shots, {total_dur}s total",
        "",
        "shots:",
    ]
    
    for shot in shots:
        # Clean characters - remove brackets for YAML
        chars = []
        for c in shot['characters']:
            c = c.strip()
            if c and c != '—':
                chars.append(c)
        
        looks = []
        for l in shot['looks']:
            l = l.strip()
            if l and l != '—':
                looks.append(l)
        
        # Parse dialogue
        dialogues = parse_dialogue(shot['dialogue_raw'])
        
        lines.append(f"  - shot_id: {shot['shot_id']}")
        lines.append(f"    scene: {shot['scene']}")
        lines.append(f"    characters: {json.dumps(chars, ensure_ascii=False)}")
        lines.append(f"    looks: {json.dumps(looks, ensure_ascii=False)}")
        lines.append(f"    shot_size: {get_shot_size_code(shot['shot_size'])}")
        lines.append(f"    duration_sec: {shot['duration']}")
        lines.append(f"    mode: {shot['mode']}")
        lines.append(f"    camera: {shot['camera']}")
        
        # Description - wrap at 80 chars
        desc = shot['description']
        lines.append(f"    description: >")
        # Simple wrapping
        desc_lines = textwrap.wrap(desc, width=76)
        for dl in desc_lines:
            lines.append(f"      {dl}")
        
        # Dialogue
        lines.append(f"    dialogue:")
        if dialogues:
            for d in dialogues:
                lines.append(f"      - speaker: {d['speaker']}")
                lines.append(f'        emotion: "{d["emotion"]}"')
                lines.append(f'        line: "{d["line"]}"')
        else:
            lines.append(f"      []")
            if '无对白' in shot['dialogue_raw'] or '（无' in shot['dialogue_raw']:
                note = shot['dialogue_raw'].replace('（', '').replace('）', '')
                lines.append(f"    note: {note}")
        
        lines.append("")
    
    return '\n'.join(lines)

def generate_segments_yaml(ep_data, shots, seg_shots):
    """Generate segments.yaml content."""
    ep = ep_data['ep']
    title = ep_data['title']
    total_dur = sum(s['duration'] for s in shots)
    
    lines = [
        f"# {ep} {title} · segments.yaml",
        f"# {len(seg_shots)} Seedance segments · {total_dur}s total",
        f"# 按 shots.yaml 镜号合并为 segment；对白与 md 引号内字面一致",
        "",
        "segments:",
    ]
    
    seg_idx = 0
    for seg_id in sorted(seg_shots.keys()):
        seg_idx += 1
        seg_shot_list = seg_shots[seg_id]
        if not seg_shot_list:
            continue
        
        seg_dur = sum(s['duration'] for s in seg_shot_list)
        shot_ids = [s['shot_id'] for s in seg_shot_list]
        
        # Get scene (should be same for all shots in segment)
        scene = seg_shot_list[0]['scene']
        
        # Extract segment title from the segment id
        seg_title = f"段落{seg_idx}"
        
        # Collect all unique characters and looks
        all_chars = []
        all_looks = []
        for s in seg_shot_list:
            for c in s['characters']:
                c = c.strip()
                if c and c != '—' and c not in all_chars:
                    all_chars.append(c)
            for l in s['looks']:
                l = l.strip()
                if l and l != '—' and l not in all_looks:
                    all_looks.append(l)
        
        # Build images section
        images = []
        img_idx = 0
        for look_id in all_looks:
            img_idx += 1
            if img_idx == 1:
                role = "图1（主角色）"
            elif look_id.startswith('SCENE-'):
                role = f"图{img_idx}（场景）"
            else:
                role = f"图{img_idx}"
            
            desc = build_look_desc(look_id)
            images.append({'role': role, 'id': look_id, 'desc': desc})
        
        # Make sure scene is last image
        scene_in_images = any(img['id'] == scene for img in images)
        if not scene_in_images:
            img_idx = len(images) + 1
            images.append({
                'role': f"图{img_idx}（场景）",
                'id': scene,
                'desc': SCENE_DESC.get(scene, scene),
            })
        
        # Collect all dialogues
        all_dialogues = []
        for s in seg_shot_list:
            all_dialogues.extend(parse_dialogue(s['dialogue_raw']))
        
        # Build seedance prompt
        prompt_lines = []
        # Image references
        for img in images:
            prompt_lines.append(f"      【{img['role'].split('（')[0].replace('图','图')}】{img['id']}·{img['desc'].split('，')[0] if '，' in img['desc'] else img['desc'][:20]}")
        
        # Actually build proper prompt with full descriptions
        prompt_lines = []
        for i, img in enumerate(images):
            role_key = f"图{i+1}"
            id_part = img['id']
            # Get short desc for the prompt
            full_desc = img['desc']
            if full_desc.startswith('苏辣辣'):
                costume = '白T+修身牛仔裤+酒红围裙+辣椒项链'
            elif full_desc.startswith('陆北辰'):
                costume = '深蓝T+深灰牛仔裤+银框眼镜+键盘帽吊坠'
            elif full_desc.startswith('林小暖'):
                costume = '藏蓝毛衣+浅色牛仔裤+帆布鞋+鲨鱼夹'
            elif full_desc.startswith('赵大鹏'):
                costume = '红色Polo衫+卡其色短裤+运动鞋'
            elif full_desc.startswith('苏爸'):
                costume = '灰T+条纹围裙+深色长裤+黑布鞋'
            elif full_desc.startswith('陆妈'):
                costume = '深红针织开衫+白色高领+黑色长裤+皮鞋'
            elif id_part.startswith('[待补：'):
                costume = '待补群演'
            elif id_part.startswith('SCENE-'):
                costume = full_desc
            else:
                costume = full_desc[:40]
            prompt_lines.append(f"      【{role_key}】{id_part}·{costume}")
        
        # Role assignments
        non_scene = [img for img in images if not img['id'].startswith('SCENE-')]
        if len(non_scene) >= 2:
            prompt_lines.append(f"      角色分工：仅图1可[动作]；图2禁止[动作]。")
        elif len(non_scene) == 1:
            prompt_lines.append(f"      角色分工：仅图1可[动作]。")
        
        # Props
        prompt_lines.append(f"      竖屏9比16连贯叙事。")
        
        # Camera shots
        shot_idx = 0
        for s in seg_shot_list:
            shot_idx += 1
            prompt_lines.append(f"      镜头{shot_idx}（{s['duration']}s）{s['shot_size']}{s['camera']}：{s['description']}")
        
        # Dialogue
        prompt_lines.append(f"      [以下对白仅供语音合成，严禁在画面中显示任何文字]")
        if all_dialogues:
            for d in all_dialogues:
                if d['speaker'] == '旁白':
                    prompt_lines.append(f"      旁白（{d['emotion']}）：「{d['line']}」")
                elif '内心' in d['emotion'] or '低声·自语' in d['emotion']:
                    prompt_lines.append(f"      独白（{d['speaker']}，{d['emotion']}）：「{d['line']}」")
                else:
                    prompt_lines.append(f"      对白（{d['speaker']}，{d['emotion']}）：「{d['line']}」")
        else:
            prompt_lines.append(f"      （无对白）")
        
        prompt_lines.append(f"      画面全程无任何文字、字幕、标题、水印。")
        prompt_lines.append(f"      {PROMPT_SUFFIX}")
        
        seedance_prompt = '\n'.join(prompt_lines)
        
        # Write segment
        lines.append(f"")
        lines.append(f"  - segment_id: {seg_id}")
        lines.append(f"    title: \"{seg_title}\"")
        lines.append(f"    scene: {scene}")
        lines.append(f"    duration_sec: {seg_dur}")
        lines.append(f"    shot_ids: {json.dumps(shot_ids, ensure_ascii=False)}")
        if seg_idx == 1:
            lines.append(f"    transition_from_prev: hard_cut")
        else:
            lines.append(f"    transition_from_prev: hard_cut")
        
        # Images
        lines.append(f"    images:")
        for img in images:
            lines.append(f"      - role: \"{img['role']}\"")
            lines.append(f"        id: {img['id']}")
            lines.append(f"        desc: \"{img['desc']}\"")
        
        # Seedance prompt
        lines.append(f"    seedance_prompt: |")
        lines.append(seedance_prompt)
    
    return '\n'.join(lines)

# Main processing
base_dir = "/Users/leifu/Movies/dramas/dramas/鸳鸯锅之恋/剧本"

for ep_data in EPISODES:
    ep = ep_data['ep']
    filepath = os.path.join(base_dir, ep_data['file'])
    
    print(f"\n{'='*60}")
    print(f"Processing {ep} - {ep_data['title']}")
    
    shots, seg_shots = parse_shots_from_md(filepath)
    
    if not shots:
        print(f"  WARNING: No shots parsed for {ep}!")
        continue
    
    print(f"  Parsed {len(shots)} shots in {len(seg_shots)} segments")
    
    # Generate shots.yaml
    shots_yaml = generate_shots_yaml(ep_data, shots)
    shots_path = os.path.join(base_dir, f"{ep}/{ep}_shots.yaml")
    with open(shots_path, 'w', encoding='utf-8') as f:
        f.write(shots_yaml)
    print(f"  Written: {shots_path}")
    
    # Generate segments.yaml
    segments_yaml = generate_segments_yaml(ep_data, shots, seg_shots)
    segs_path = os.path.join(base_dir, f"{ep}/{ep}_segments.yaml")
    with open(segs_path, 'w', encoding='utf-8') as f:
        f.write(segments_yaml)
    print(f"  Written: {segs_path}")
    
    # Validation
    total_dur = sum(s['duration'] for s in shots)
    print(f"  Duration: {total_dur}s | Shots: {len(shots)} | Segments: {len(seg_shots)}")
    if total_dur < 75 or total_dur > 120:
        print(f"  ⚠️ Duration out of range (75-120s)!")
    if len(shots) < 8 or len(shots) > 12:
        print(f"  ⚠️ Shot count out of range (8-12)!")
    if len(seg_shots) < 6 or len(seg_shots) > 10:
        print(f"  ⚠️ Segment count out of range (6-10)!")

print(f"\n{'='*60}")
print("All 6 episodes processed. Generating validation report...")
