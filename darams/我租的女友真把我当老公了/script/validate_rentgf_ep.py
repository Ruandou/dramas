#!/usr/bin/env python3
"""Validate EP storyboard: shots.yaml vs segments.yaml consistency."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_ep(ep: str) -> int:
    ep_dir = ROOT / "剧本" / ep
    shots_path = ep_dir / f"{ep}_shots.yaml"
    segs_path = ep_dir / f"{ep}_segments.yaml"
    if not shots_path.exists() or not segs_path.exists():
        print(f"MISSING: {ep_dir}")
        return 1

    shots = load_yaml(shots_path)["shots"]
    segs = load_yaml(segs_path)["segments"]
    shot_map = {s["shot_id"]: s for s in shots}
    errors: list[str] = []

    for seg in segs:
        sid = seg["segment_id"]
        ids = seg["shot_ids"]
        missing = [i for i in ids if i not in shot_map]
        if missing:
            errors.append(f"{sid}: unknown shots {missing}")
            continue
        shot_sum = sum(shot_map[i].get("duration_sec") or 0 for i in ids)
        dur = seg["duration_sec"]
        # skip-only segment (e.g. preview card): shot sum 0, API dur > 0 OK
        if shot_sum == 0 and all(shot_map[i].get("mode") == "skip" for i in ids):
            if dur < 4 or dur > 12:
                errors.append(f"{sid}: skip-only segment duration {dur}s out of 4-12")
            continue
        if shot_sum != dur:
            errors.append(f"{sid}: shot sum {shot_sum}s != duration_sec {dur}s")
        if dur < 4 or dur > 12:
            errors.append(f"{sid}: duration_sec {dur}s out of Seedance 4-12 limit")

    for s in shots:
        if s.get("mode") == "i2v_ref" and "api" in s:
            if not s["api"].get("return_last_frame"):
                errors.append(f"{s['shot_id']}: i2v_ref missing return_last_frame")

    total = sum(s["duration_sec"] for s in segs)
    print(f"{ep}: {len(shots)} shots, {len(segs)} segments, total API {total}s")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        return 1
    print("  OK")
    return 0


def main() -> None:
    eps = sys.argv[1:] or ["EP01"]
    code = 0
    for ep in eps:
        ep = ep.upper()
        if not ep.startswith("EP"):
            ep = f"EP{ep.zfill(2)}"
        code |= validate_ep(ep)
    sys.exit(code)


if __name__ == "__main__":
    main()
