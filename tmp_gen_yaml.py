#!/usr/bin/env python3
"""批量为72集生成 shots.yaml 和 segments.yaml"""
import re, os, json, sys
from pathlib import Path

PROJECT = Path("dramas/重来一次我不想再忍了")

def parse_episode(ep_num):
    ep_dir = PROJECT / "剧本" / f"EP{ep_num:02d}"
    md_files = list(ep_dir.glob("EP*.md"))
    if not md_files:
        return None
    md = md_files[0].read_text(encoding="utf-8")
    
    segs = re.split(r'^## SEG-\d+', md, flags=re.MULTILINE)
    segs = [s.strip() for s in segs if s.strip() and s.strip().startswith('·')]
    
    segments = []
    total_shots = 0
    total_dur = 0
    
    # If no SEG headers found, try parsing the table directly
    if not segs:
        return parse_table_direct(md, ep_num)
    
    for i, seg_text in enumerate(segs):
        lines = seg_text.split('\n')
        header_line = lines[0] if lines else ""
        
        # Parse scene from header
        scene_match = re.search(r'SCENE-(\d+)', header_line)
        scene_id = f"SCENE-{scene_match.group(1)}" if scene_match else "SCENE-001"
        
        seg_desc = header_line.split('·')[-1].strip() if '·' in header_line else ""
        
        shots = []
        in_table = False
        for line in lines:
            if '| 镜号' in line or '|------' in line:
                in_table = True
                continue
            if in_table and line.startswith('|'):
                cols = [c.strip() for c in line.split('|')]
                if len(cols) >= 6:
                    shot_id = f"EP{ep_num:02d}-S{len(total_shots_dummy = shots) + 1:02d}"
                    try:
                        dur = int(cols[5].strip())
                    except:
                        dur = 6
                    desc = cols[3] if len(cols) > 3 else ""
                    seg_total_dur += dur
                    shots.append({
                        "id": shot_id,
                        "type": cols[2] if len(cols) > 2 else "中景",
                        "duration_sec": dur,
                        "description": desc[:200]
                    })
        
        if shots:
            seg_dur = sum(s["duration_sec"] for s in shots)
            segments.append({
                "id": f"EP{ep_num:02d}-SEG{i+1:02d}",
                "scene_id": scene_id,
                "description": seg_desc[:100],
                "shots": shots,
                "total_duration_sec": seg_dur
            })
            total_shots += len(shots)
            total_dur += seg_dur
    
    return {"segments": segments, "total_shots": total_shots, "total_duration_sec": total_dur}

def parse_table_direct(md, ep_num):
    """Fallback: parse table rows directly"""
    segments = []
    shots = []
    current_seg = None
    total_dur = 0
    
    lines = md.split('\n')
    in_table = False
    
    for line in lines:
        if '| 镜号' in line or '|------' in line and 'duration' in md:
            in_table = True
            continue
        if line.startswith('#') and shots:
            # End of table section
            if shots:
                seg_dur = sum(s["duration_sec"] for s in shots)
                segments.append({
                    "id": f"EP{ep_num:02d}-SEG{len(segments)+1:02d}",
                    "scene_id": "SCENE-001",
                    "description": "",
                    "shots": shots,
                    "total_duration_sec": seg_dur
                })
                shots = []
            continue
            
        if in_table and line.startswith('|'):
            cols = [c.strip() for c in line.split('|')]
            if len(cols) >= 6 and cols[1].strip().isdigit():
                try:
                    dur = int(cols[5].strip())
                except:
                    dur = 6
                total_dur += dur
                shots.append({
                    "id": f"EP{ep_num:02d}-S{len(shots)+1:02d}",
                    "type": cols[2] if len(cols) > 2 else "中景",
                    "duration_sec": dur,
                    "description": cols[3][:200] if len(cols) > 3 else ""
                })
    
    if shots:
        seg_dur = sum(s["duration_sec"] for s in shots)
        segments.append({
            "id": f"EP{ep_num:02d}-SEG{len(segments)+1:02d}",
            "scene_id": "SCENE-001",
            "description": "",
            "shots": shots,
            "total_duration_sec": seg_dur
        })
    
    total_shots = len(shots)
    return {"segments": segments, "total_shots": total_shots, "total_duration_sec": total_dur}

def main():
    os.chdir("/Users/leifu/Movies/dramas")
    
    for ep in range(1, 73):
        ep_dir = PROJECT / "剧本" / f"EP{ep:02d}"
        data = parse_episode(ep)
        if not data or not data["segments"]:
            print(f"EP{ep:02d}: SKIP (no parseable data)")
            continue
        
        # Write segments.yaml
        seg_data = {
            "episode": f"EP{ep:02d}",
            "segments": data["segments"],
            "total_segments": len(data["segments"]),
            "total_shots": data["total_shots"],
            "total_duration_sec": data["total_duration_sec"]
        }
        seg_path = ep_dir / f"EP{ep:02d}_segments.yaml"
        with open(seg_path, "w", encoding="utf-8") as f:
            yaml_content = f"# EP{ep:02d} segments.yaml\n"
            yaml_content += f"episode: EP{ep:02d}\n"
            yaml_content += f"total_duration_sec: {data['total_duration_sec']}\n"
            yaml_content += f"total_shots: {data['total_shots']}\n"
            yaml_content += "segments:\n"
            for seg in data["segments"]:
                yaml_content += f"  - id: {seg['id']}\n"
                yaml_content += f"    scene_id: {seg['scene_id']}\n"
                yaml_content += f"    description: \"{seg['description']}\"\n"
                yaml_content += f"    total_duration_sec: {seg['total_duration_sec']}\n"
                yaml_content += "    shots:\n"
                for s in seg["shots"]:
                    yaml_content += f"      - id: {s['id']}\n"
                    yaml_content += f"        type: \"{s['type']}\"\n"
                    yaml_content += f"        duration_sec: {s['duration_sec']}\n"
                    yaml_content += f"        description: \"{s['description']}\"\n"
            f.write(yaml_content)
        
        # Write shots.yaml
        shots_data = {
            "episode": f"EP{ep:02d}",
            "shots": [],
            "total_duration_sec": data["total_duration_sec"]
        }
        for seg in data["segments"]:
            for s in seg["shots"]:
                s["scene_id"] = seg["scene_id"]
                s["seg_id"] = seg["id"]
                shots_data["shots"].append(s)
        
        shots_path = ep_dir / f"EP{ep:02d}_shots.yaml"
        with open(shots_path, "w", encoding="utf-8") as f:
            yaml_content = f"# EP{ep:02d} shots.yaml\n"
            yaml_content += f"episode: EP{ep:02d}\n"
            yaml_content += f"total_duration_sec: {data['total_duration_sec']}\n"
            yaml_content += f"total_shots: {data['total_shots']}\n"
            yaml_content += "shots:\n"
            for s in shots_data["shots"]:
                yaml_content += f"  - id: {s['id']}\n"
                yaml_content += f"    scene_id: {s['scene_id']}\n"
                yaml_content += f"    seg_id: {s['seg_id']}\n"
                yaml_content += f"    type: \"{s['type']}\"\n"
                yaml_content += f"    duration_sec: {s['duration_sec']}\n"
                yaml_content += f"    description: \"{s['description']}\"\n"
            f.write(yaml_content)
        
        print(f"EP{ep:02d}: {len(data['segments'])} segs, {data['total_shots']} shots, {data['total_duration_sec']}s")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
