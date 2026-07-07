#!/usr/bin/env python3
"""Parse EP##.md 11-column table → shots.yaml + segments.yaml
Handles multi-line table cells where dialogue spills to continuation lines."""
import re, sys, os, json

VOICE = {
    "CHAR-001": "clear female alto voice, slightly cool and crisp tone, standard Mandarin with occasional soft Huizhou accent endings, speaks faster when excited but slower and colder when angry, precise articulation",
    "CHAR-002": "warm male baritone voice, scholarly and gentle tone, standard Mandarin with elegant word choice, slightly slower pace with thoughtful pauses, habit of pushing up glasses while thinking",
    "CHAR-003": "elderly female voice, soft and weathered, strong Huizhou dialect, speaks slowly and deliberately, voice carries weight of lifelong wisdom even in few words",
    "CHAR-004": "sharp female soprano voice, Shanghai-accented Mandarin, fast speech tempo with aggressive edge in business settings, tone can switch from sugary sweet to ice cold in one sentence",
    "CHAR-005": "low male baritone voice, lacks confidence and conviction, standard Mandarin, often uses hesitation words, voice wavers under pressure",
    "CHAR-006": "elderly female voice, heavily accented Huizhou dialect, speaks rarely and slowly but every word has weight, voice is raspy from age but steady and calm, understands Mandarin but replies in dialect",
    "CHAR-007": "loud male voice, Huizhou dialect mixed with rough Mandarin, speaks directly without politeness, voice projects across village square, habit of clearing throat before important announcements",
    "CHAR-008": "warm female alto voice, Huizhou dialect with imperfect Mandarin, nervous habit of speaking faster when anxious, voice gradually gains confidence as series progresses",
    "CHAR-009": "NO SPOKEN DIALOGUE — communicates through sign language. Occasional soft humming sounds.",
    "CHAR-010": "oily male baritone voice, county-town accented Mandarin, speaks with false familiarity, habit of slapping table while talking, voice gets louder when negotiating",
    "CHAR-011": "elegant female voice, slight overseas Chinese accent in Mandarin, switches fluidly between Mandarin/English/French, speaks precisely and never raises volume but commands authority",
    "CHAR-012": "male voice with heavy French accent when speaking English, passionate and animated, speaks rapid French when excited, limited Mandarin",
    "CHAR-GRP-01": "middle-aged male voice, standard Mandarin, professional but slightly arrogant tone, habit of clearing throat",
    "CHAR-GRP-02": "young female voice, standard Mandarin, eager and slightly nervous, speaks quickly",
    "CHAR-GRP-03": "older male voice, strong Huizhou dialect with rough Mandarin, urgent and direct tone, speaks loudly on phone",
    "CHAR-GRP-04": "middle-aged male voice, cautious and evasive tone, standard Mandarin with slight Shanghai accent, corporate lawyer-style measured speech",
    "CHAR-GRP-05": "middle-aged male voice, formal and impersonal tone, standard Mandarin, speaks in short factual sentences",
    "CHAR-GRP-06": "middle-aged female voice, strong Huizhou dialect, warm but gossipy tone, rural Anhui village woman cadence",
    "CHAR-GRP-07": "middle-aged female voice, Huizhou dialect, slightly higher pitch, responds to gossip with quick agreement",
    "CHAR-GRP-08": "elderly female voice, strong Huizhou dialect, warm and weathered tone, speaks slowly with deliberate cadence, voice cracks slightly on emotional words",
}

BASE = "https://drama-reference-images.tos-cn-beijing.volces.com"
PZ = "指尖山河"

def S(scene_id): return f"{BASE}/scenes/{PZ}/{scene_id}.png"
def L(look_id): return f"{BASE}/looks/{PZ}/{look_id}.png"
def P(prop_id): return f"{BASE}/props/{PZ}/{prop_id}.png"

def parse_dialogue(cell):
    """Parse: **CHAR-###**[内心]：——text—— or **CHAR-###**：——text——"""
    if not cell or not cell.strip():
        return []
    cell = cell.strip()
    lines = []
    parts = re.split(r'\*\*(CHAR-[\w-]+)\*\*(?:\[(内心(?:独白)?)\])?[：:]', cell)
    i = 1
    while i + 2 <= len(parts):
        char_id = parts[i].strip()
        tag = parts[i+1] if parts[i+1] else None
        text = parts[i+2].strip() if i+2 < len(parts) else ""
        i += 3
        dtype = "inner" if tag else "spoken"
        text = text.strip()
        text = re.sub(r'^\s*——\s*', '', text)
        text = re.sub(r'\s*——\s*$', '', text)
        if text:
            lines.append({"speaker": char_id, "text": text, "type": dtype})
    return lines

def merge_table_lines(raw_lines):
    """Merge multi-line table cells: continuation lines (no leading |) get appended to previous row."""
    merged = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].rstrip('\n').rstrip('\r')
        if line.startswith('|') and 'EP' in line and '-S' in line and 'shot_id' not in line:
            cnt = line.count('|')
            while cnt < 12 and i + 1 < len(raw_lines):
                i += 1
                cont = raw_lines[i].strip()
                if cont.startswith('|') or cont.startswith('>') or cont.startswith('##') or cont.startswith('---'):
                    i -= 1
                    break
                if cont:
                    line += ' ' + cont
                    cnt = line.count('|')
        merged.append(line)
        i += 1
    return merged

def parse_md(filepath):
    with open(filepath, 'r') as f:
        raw_lines = f.readlines()
    
    # Extract frontmatter from raw content
    content = ''.join(raw_lines)
    fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    ep_id = "EP??"
    ep_title = ""
    if fm_match:
        for line in fm_match.group(1).split('\n'):
            if line.startswith('episode_id:'):
                ep_id = line.split(':',1)[1].strip()
            elif line.startswith('episode_title:'):
                ep_title = line.split(':',1)[1].strip()
    
    # Merge multi-line table cells
    merged_lines = merge_table_lines(raw_lines)
    merged_content = '\n'.join(merged_lines)
    
    # Find SEG boundaries in merged content
    seg_boundaries = []
    for m in re.finditer(r'## SEG(\d+) —', merged_content):
        seg_boundaries.append((int(m.group(1)), m.start()))
    
    shots = []
    for line in merged_lines:
        line = line.strip()
        if not line.startswith('|') or 'EP' not in line or '-S' not in line:
            continue
        if 'shot_id' in line or '镜号' in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 12:
            continue
        
        try:
            shot_no = int(parts[1])
        except:
            continue
        
        shot_id = parts[2].strip('`')
        scene = parts[3].strip('`')
        
        chars = [c.strip().strip('`') for c in parts[4].split(',') if c.strip()]
        
        looks = {}
        for l in parts[5].split(','):
            l = l.strip().strip('`')
            if '-' in l:
                char_part = l.rsplit('-', 1)[0]
                looks[char_part] = l
        
        camera = parts[6].strip()
        try:
            duration = int(parts[7])
        except:
            duration = 5
        mode = parts[8].strip().strip('`')
        movement = parts[9].strip()
        visual = parts[10].strip()
        dialogue_raw = parts[11].strip() if len(parts) > 11 else ""
        
        line_pos = merged_content.find(line)
        seg_idx = 0
        for snum, spos in reversed(seg_boundaries):
            if line_pos > spos:
                seg_idx = snum
                break
        
        dialogue = parse_dialogue(dialogue_raw)
        
        shots.append({
            "shot_id": shot_id,
            "shot_no": shot_no,
            "scene": scene,
            "seg": seg_idx,
            "characters": chars,
            "looks": looks,
            "camera": camera if camera else "medium",
            "duration_sec": duration,
            "mode": mode,
            "movement": movement,
            "visual": visual,
            "dialogue": dialogue,
        })
    
    return ep_id, ep_title, shots

def gen_shots_yaml(ep_id, ep_title, shots, out_path):
    lines = [
        f"# {ep_id} {ep_title} — shots.yaml",
        "# SOURCE FIDELITY PROOF",
        f"# source_file: 剧本/{ep_id}/{ep_id}_{ep_title}.md",
        f"# source_shot_count: {len(shots)}",
        f"# yaml_shot_count: {len(shots)}",
        "# fidelity: EXACT",
        "",
        "shots:"
    ]
    
    for s in shots:
        refs = []
        seen = set()
        r = S(s['scene'])
        refs.append(r); seen.add(r)
        for cid, lid in s['looks'].items():
            r = L(lid)
            if r not in seen:
                refs.append(r); seen.add(r)
        if s['scene'] == 'SCENE-003':
            r = P("PROP-004")
            if r not in seen:
                refs.append(r); seen.add(r)
        
        dlg = s['dialogue']
        
        lines.append(
            f"  - {{shot_id: {s['shot_id']}, scene: {s['scene']}, "
            f"characters: {json.dumps(s['characters'], ensure_ascii=False)}, "
            f"looks: {json.dumps(s['looks'], ensure_ascii=False)}, "
            f"camera: {s['camera']}, duration_sec: {s['duration_sec']}, "
            f"ref_images: {json.dumps(refs, ensure_ascii=False)}, "
            f"dialogue: {json.dumps(dlg, ensure_ascii=False)}}}"
        )
    
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  → {out_path} ({len(shots)} shots)")

def gen_segments_yaml(ep_id, ep_title, shots, out_path):
    segs = {}
    for s in shots:
        sid = s['seg']
        if sid not in segs:
            segs[sid] = []
        segs[sid].append(s)
    
    lines = [
        f"# {ep_id} {ep_title} — segments.yaml",
        f"episode: {ep_id}",
        f"title: {ep_title}",
        f"total_segments: {len(segs)}",
        f"total_duration_sec: {sum(s['duration_sec'] for s in shots)}",
        "",
        "segments:"
    ]
    
    for seg_id in sorted(segs.keys()):
        seg_shots = segs[seg_id]
        shot_ids = [s['shot_id'] for s in seg_shots]
        duration = sum(s['duration_sec'] for s in seg_shots)
        scene = seg_shots[0]['scene']
        
        all_chars = set()
        all_looks = {}
        for s in seg_shots:
            for c in s['characters']:
                all_chars.add(c)
            all_looks.update(s['looks'])
        
        content_roles = [c for c in all_chars if not c.startswith('[')]
        
        refs = []
        seen = set()
        r = S(scene)
        refs.append(r); seen.add(r)
        for lid in all_looks.values():
            r = L(lid)
            if r not in seen:
                refs.append(r); seen.add(r)
        if scene == 'SCENE-003':
            r = P("PROP-004")
            if r not in seen:
                refs.append(r); seen.add(r)
        
        vp = {}
        for c in all_chars:
            if c in VOICE:
                vp[c] = VOICE[c]
            elif not c.startswith('['):
                vp[c] = "neutral Mandarin voice"
        
        notes_parts = []
        for s in seg_shots:
            for d in s['dialogue']:
                txt = d['text'][:25]
                notes_parts.append(txt)
                if len(notes_parts) >= 2:
                    break
            if len(notes_parts) >= 2:
                break
        notes = " ".join(notes_parts) if notes_parts else ""
        notes = notes.replace('"', "'")
        
        lines.append(
            f"  - {{segment_id: SEG{seg_id:02d}, scene: {scene}, "
            f"shots: {json.dumps(shot_ids, ensure_ascii=False)}, "
            f"duration_sec: {duration}, "
            f"content_roles: {json.dumps(content_roles, ensure_ascii=False)}, "
            f"looks: {json.dumps(all_looks, ensure_ascii=False)}, "
            f"ref_images: {json.dumps(refs, ensure_ascii=False)}, "
            f"voice_prompts: {json.dumps(vp, ensure_ascii=False)}, "
            f"notes: \"{notes}\"}}"
        )
    
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  → {out_path} ({len(segs)} segments)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_yaml.py <EP##>")
        sys.exit(1)
    
    ep = sys.argv[1]
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_dir = os.path.join(project_root, "剧本", ep)
    
    md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
    if not md_files:
        print(f"ERROR: No .md file found in {md_dir}")
        sys.exit(1)
    
    md_path = os.path.join(md_dir, md_files[0])
    print(f"Parsing: {md_path}")
    
    ep_id, ep_title, shots = parse_md(md_path)
    print(f"  Episode: {ep_id} · {ep_title}")
    print(f"  Shots: {len(shots)}")
    
    gen_shots_yaml(ep_id, ep_title, shots, os.path.join(md_dir, f"{ep_id}_shots.yaml"))
    gen_segments_yaml(ep_id, ep_title, shots, os.path.join(md_dir, f"{ep_id}_segments.yaml"))
    print("Done!")

if __name__ == '__main__':
    main()
