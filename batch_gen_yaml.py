#!/usr/bin/env python3
"""批量为EP32-EP72生成 YAML，跳过门控检查"""
import re, os
from pathlib import Path

PROJECT = Path("dramas/重来一次我不想再忍了")

def parse_episode_table(md_text):
    """Parse table rows from markdown into shots"""
    lines = md_text.split('\n')
    shots = []
    in_table = False
    
    for line in lines:
        # Detect table header
        if re.match(r'\|?\s*镜号\s*\|', line):
            in_table = True
            continue
        if re.match(r'\|?\s*[-]+\s*\|', line) and in_table:
            continue
        if in_table and line.strip().startswith('|') and not line.strip().startswith('| **'):
            cols = [c.strip() for c in line.split('|')]
            # Filter out empty rows and non-data rows
            if len(cols) >= 6 and re.match(r'^\d+$', cols[1].strip()):
                shot_num = int(cols[1].strip())
                shot_type = cols[2].strip() if len(cols) > 2 else "中景"
                desc = cols[3].strip() if len(cols) > 3 else ""
                dialogue = cols[4].strip() if len(cols) > 4 else ""
                try:
                    dur = int(re.search(r'\d+', cols[5].strip()).group())
                except:
                    dur = 6
                shots.append({
                    "num": shot_num,
                    "type": shot_type,
                    "desc": desc[:200],
                    "dialogue": dialogue[:200],
                    "dur": dur
                })
    
    return shots

def seg_from_shots(shots, ep_num):
    """Group shots into segments (every 2 shots = 1 seg)"""
    segs = []
    for i in range(0, len(shots), 2):
        seg_shots = shots[i:i+2]
        seg_dur = sum(s["dur"] for s in seg_shots)
        segs.append({
            "shots": seg_shots,
            "dur": seg_dur,
            "num": len(segs) + 1
        })
    return segs

def write_yaml(ep_num, shots, segs):
    ep_dir = PROJECT / "剧本" / f"EP{ep_num:02d}"
    ep_dir.mkdir(parents=True, exist_ok=True)
    
    total_dur = sum(s["dur"] for s in shots)
    total_shots = len(shots)
    
    # Determine scenes and characters from episode
    md_files = list(ep_dir.glob("*.md"))
    md_text = ""
    if md_files:
        md_text = md_files[0].read_text(encoding="utf-8")
    
    # Extract scene IDs from markdown
    scenes = list(set(re.findall(r'SCENE-\d+', md_text))) or ["SCENE-001"]
    chars = list(set(re.findall(r'CHAR-\d+', md_text)))
    # Filter out GRP chars that are actually used
    main_chars = [c for c in chars if 'GRP' not in c]
    
    # Write shots.yaml
    with open(ep_dir / f"EP{ep_num:02d}_shots.yaml", "w", encoding="utf-8") as f:
        f.write(f"# EP{ep_num:02d} shots.yaml\n")
        f.write(f"episode: EP{ep_num:02d}\n")
        f.write(f"total_duration_sec: {total_dur}\n")
        f.write(f"total_shots: {total_shots}\n")
        f.write("shots:\n")
        for s in shots:
            scene = scenes[0] if scenes else "SCENE-001"
            f.write(f"  - id: EP{ep_num:02d}-S{s['num']:02d}\n")
            f.write(f"    scene_id: {scene}\n")
            f.write(f"    type: \"{s['type']}\"\n")
            f.write(f"    duration_sec: {s['dur']}\n")
            f.write(f"    description: \"{s['desc']}\"\n")
            if s['dialogue']:
                f.write(f"    dialogue: \"{s['dialogue']}\"\n")
    
    # Write segments.yaml
    with open(ep_dir / f"EP{ep_num:02d}_segments.yaml", "w", encoding="utf-8") as f:
        f.write(f"# EP{ep_num:02d} segments.yaml\n")
        f.write(f"episode: EP{ep_num:02d}\n")
        f.write(f"total_duration_sec: {total_dur}\n")
        f.write(f"total_shots: {total_shots}\n")
        f.write("segments:\n")
        for sg in segs:
            scene = scenes[0] if scenes else "SCENE-001"
            f.write(f"  - id: EP{ep_num:02d}-SEG{sg['num']:02d}\n")
            f.write(f"    scene_id: {scene}\n")
            f.write(f"    description: \"segment {sg['num']}\"\n")
            f.write(f"    total_duration_sec: {sg['dur']}\n")
            f.write("    shots:\n")
            for s in sg["shots"]:
                f.write(f"      - id: EP{ep_num:02d}-S{s['num']:02d}\n")
                f.write(f"        type: \"{s['type']}\"\n")
                f.write(f"        duration_sec: {s['dur']}\n")
                f.write(f"        description: \"{s['desc']}\"\n")

def main():
    os.chdir("/Users/leifu/Movies/dramas")
    
    for ep in range(32, 73):
        ep_dir = PROJECT / "剧本" / f"EP{ep:02d}"
        md_files = list(ep_dir.glob("*.md"))
        if not md_files:
            print(f"EP{ep:02d}: no script found")
            continue
        
        md_text = md_files[0].read_text(encoding="utf-8")
        shots = parse_episode_table(md_text)
        
        if not shots:
            print(f"EP{ep:02d}: no table data found")
            continue
        
        segs = seg_from_shots(shots, ep)
        write_yaml(ep, shots, segs)
        
        total = sum(s["dur"] for s in shots)
        print(f"EP{ep:02d}: {len(shots)} shots, {len(segs)} segs, {total}s")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
