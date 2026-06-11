#!/usr/bin/env python3
"""G5 Gate Compliance Checker for 断剑归尘 EP02-EP06."""

import sys
import re
import yaml
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
VALID_CHARS = {f"CHAR-{i:03d}" for i in range(1, 15)} | {"NARRATOR"}
VALID_SCENES = {f"SCENE-{i:03d}" for i in range(1, 14)}
VALID_PROPS = {f"PROP-{i:03d}" for i in range(1, 10)}

# Hard constraints
MIN_SEGMENTS = 12
MAX_SEGMENTS = 15
MIN_DURATION = 4
MAX_DURATION = 12
MAX_DURATION_2SHOT = 14
MIN_TOTAL = 140
MAX_TOTAL = 200
MIN_DIALOGUE = 50
MAX_MONOLOGUE = 8
MIN_DENSITY = 20.0


def get_duration(seg):
    d = seg.get("duration_sec")
    if d is not None:
        return int(d)
    d = seg.get("duration")
    if d is not None:
        if isinstance(d, str):
            return int(d.rstrip("s"))
        return int(d)
    return 0


def get_shot_ids(seg):
    return seg.get("shot_ids") or seg.get("shots") or []


def extract_dialogue_from_shots(shots_data):
    """Extract all dialogue lines from shots yaml."""
    lines = []
    shots = shots_data if isinstance(shots_data, list) else shots_data.get("shots", [])
    for shot in shots:
        dialogue = shot.get("dialogue", [])
        if dialogue:
            for d in dialogue:
                lines.append(d)
    return lines


def check_episode(ep_num, errors, warnings):
    ep_str = f"EP{ep_num:02d}"
    base = PROJECT / "剧本" / ep_str
    shots_file = base / f"{ep_str}_shots.yaml"
    segs_file = base / f"{ep_str}_segments.yaml"

    print(f"\n{'='*60}")
    print(f"  Checking {ep_str}")
    print(f"{'='*60}")

    # Load files
    try:
        with open(shots_file, "r", encoding="utf-8") as f:
            shots_data = yaml.safe_load(f)
        shots_list = shots_data.get("shots", shots_data) if isinstance(shots_data, dict) else shots_data
    except Exception as e:
        errors.append(f"{ep_str}: shots.yaml parse error: {e}")
        print(f"  ❌ shots.yaml parse error: {e}")
        return

    try:
        with open(segs_file, "r", encoding="utf-8") as f:
            segs_data = yaml.safe_load(f)
        segments = segs_data.get("segments", segs_data) if isinstance(segs_data, dict) else segs_data
        if not isinstance(segments, list):
            segments = [segments]
    except Exception as e:
        errors.append(f"{ep_str}: segments.yaml parse error: {e}")
        print(f"  ❌ segments.yaml parse error: {e}")
        return

    # 1. Segment count
    seg_count = len(segments)
    if seg_count < MIN_SEGMENTS or seg_count > MAX_SEGMENTS:
        errors.append(f"{ep_str}: Segment count {seg_count} outside [{MIN_SEGMENTS},{MAX_SEGMENTS}]")
        print(f"  ❌ Segments: {seg_count} (need {MIN_SEGMENTS}-{MAX_SEGMENTS})")
    else:
        print(f"  ✅ Segments: {seg_count}")

    # 2. Per-segment duration
    total_dur = 0
    dur_issues = []
    for i, seg in enumerate(segments):
        dur = get_duration(seg)
        total_dur += dur
        shot_ids = get_shot_ids(seg)
        n_shots = len(shot_ids)
        max_d = MAX_DURATION_2SHOT if n_shots >= 2 else MAX_DURATION
        if dur < MIN_DURATION or dur > max_d:
            seg_id = seg.get("segment_id", f"SEG{i+1:02d}")
            dur_issues.append(f"{seg_id}: {dur}s ({n_shots} shots, max {max_d}s)")
    if dur_issues:
        for d in dur_issues:
            errors.append(f"{ep_str}: Duration violation: {d}")
            print(f"  ❌ {d}")
    else:
        print(f"  ✅ Per-segment duration: all within bounds")

    # 3. Total duration
    if total_dur < MIN_TOTAL or total_dur > MAX_TOTAL:
        errors.append(f"{ep_str}: Total duration {total_dur}s outside [{MIN_TOTAL},{MAX_TOTAL}]")
        print(f"  ❌ Total duration: {total_dur}s (need {MIN_TOTAL}-{MAX_TOTAL})")
    else:
        print(f"  ✅ Total duration: {total_dur}s")

    # 4. Dialogue from shots
    dialogue_lines = extract_dialogue_from_shots(shots_list)
    total_dialogue = len(dialogue_lines)
    monologue_count = sum(1 for d in dialogue_lines if d.get("type") == "inner_monologue" or d.get("type") == "aside")

    if total_dialogue < MIN_DIALOGUE:
        errors.append(f"{ep_str}: Dialogue count {total_dialogue} < {MIN_DIALOGUE}")
        print(f"  ❌ Dialogue: {total_dialogue} (need ≥{MIN_DIALOGUE})")
    else:
        print(f"  ✅ Dialogue: {total_dialogue}")

    if monologue_count > MAX_MONOLOGUE:
        errors.append(f"{ep_str}: Inner monologue {monologue_count} > {MAX_MONOLOGUE}")
        print(f"  ❌ Inner monologue: {monologue_count} (max {MAX_MONOLOGUE})")
    else:
        print(f"  ✅ Inner monologue: {monologue_count} (≤{MAX_MONOLOGUE})")

    # 5. Dialogue density
    if total_dur > 0:
        density = total_dialogue / (total_dur / 60.0)
        if density < MIN_DENSITY:
            errors.append(f"{ep_str}: Dialogue density {density:.1f} lines/min < {MIN_DENSITY}")
            print(f"  ❌ Density: {density:.1f} lines/min (need ≥{MIN_DENSITY})")
        else:
            print(f"  ✅ Density: {density:.1f} lines/min")

    # 6. ID validation — speakers
    invalid_speakers = set()
    for d in dialogue_lines:
        speaker = d.get("speaker", "")
        if speaker and speaker not in VALID_CHARS:
            invalid_speakers.add(speaker)
    if invalid_speakers:
        for s in sorted(invalid_speakers):
            errors.append(f"{ep_str}: Invalid speaker: {s}")
            print(f"  ❌ Invalid speaker: {s}")
    else:
        print(f"  ✅ All speakers valid CHAR-IDs")

    # 7. ID validation — scenes in segments
    invalid_scenes = set()
    for seg in segments:
        scene = seg.get("scene", "")
        if scene and scene not in VALID_SCENES:
            invalid_scenes.add(scene)
    if invalid_scenes:
        for s in sorted(invalid_scenes):
            errors.append(f"{ep_str}: Invalid scene ID: {s}")
            print(f"  ❌ Invalid scene: {s}")
    else:
        print(f"  ✅ All scene IDs valid")

    # 8. ID validation — props in shots
    invalid_props = set()
    shots = shots_list if isinstance(shots_list, list) else shots_list.get("shots", [])
    for shot in shots:
        props = shot.get("props", [])
        for p in props:
            if p not in VALID_PROPS:
                invalid_props.add(p)
    if invalid_props:
        for p in sorted(invalid_props):
            errors.append(f"{ep_str}: Invalid prop ID: {p}")
            print(f"  ❌ Invalid prop: {p}")
    else:
        print(f"  ✅ All prop IDs valid")

    # 9. Shot ID coverage — segments reference shots that exist
    shot_ids_in_shots = set()
    for shot in shots:
        sid = shot.get("shot_id", "")
        if sid:
            shot_ids_in_shots.add(sid)

    shot_ids_in_segs = set()
    for seg in segments:
        for sid in get_shot_ids(seg):
            shot_ids_in_segs.add(sid)

    missing = shot_ids_in_segs - shot_ids_in_shots
    if missing:
        for m in sorted(missing):
            errors.append(f"{ep_str}: Segment references missing shot: {m}")
            print(f"  ❌ Missing shot in shots.yaml: {m}")
    else:
        print(f"  ✅ Shot ID coverage: all segment shots exist")


def main():
    errors = []
    warnings = []

    print("G5 Gate Compliance Check — 断剑归尘 EP02-EP06")
    print(f"Project: {PROJECT}")

    for ep in range(2, 7):
        check_episode(ep, errors, warnings)

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print(f"\n  ❌ ERRORS:")
        for e in errors:
            print(f"    - {e}")
    if warnings:
        print(f"\n  ⚠️  WARNINGS:")
        for w in warnings:
            print(f"    - {w}")

    if not errors and not warnings:
        print(f"\n  ✅ ALL PASS — G5 gate cleared for EP02-EP06")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
