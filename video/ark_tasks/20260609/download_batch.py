#!/usr/bin/env python3
"""Batch download all succeeded June 9 Seedance tasks from tasks.json"""
import json, subprocess, time
from pathlib import Path

SCRIPT = Path("/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedance_video.py")
OUT_DIR = Path(__file__).resolve().parent
TASKS_PATH = Path("/Users/leifu/Movies/dramas/tasks.json")

tasks = json.loads(TASKS_PATH.read_text())
june9 = [t for t in tasks["items"] if "20260609" in t["id"] and t["status"] == "succeeded"]
print(f"Found {len(june9)} succeeded tasks from June 9")

ok = 0
fail = 0
for i, t in enumerate(june9):
    tid = t["id"]
    duration = t.get("duration", "?")
    fname = f"{i+1:02d}_{tid}.mp4"
    out = OUT_DIR / fname
    
    if out.exists():
        print(f"[{i+1}/{len(june9)}] SKIP {fname} (exists)")
        ok += 1
        continue
    
    print(f"[{i+1}/{len(june9)}] Downloading {tid} ({duration}s)...", end=" ", flush=True)
    r = subprocess.run(
        ["python3", str(SCRIPT), "download", "--task-id", tid, "-o", str(out)],
        capture_output=True, text=True, timeout=120,
        cwd=str(SCRIPT.parent)
    )
    if r.returncode == 0:
        size_mb = out.stat().st_size / 1024 / 1024 if out.exists() else 0
        print(f"OK ({size_mb:.1f}MB)")
        ok += 1
    else:
        print(f"FAIL: {r.stderr.strip() or r.stdout.strip()}")
        fail += 1
    
    time.sleep(0.3)

print(f"\nDone: {ok} succeeded, {fail} failed, {len(june9)} total")
