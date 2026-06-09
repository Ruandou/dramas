#!/usr/bin/env python3
"""Poll and download EP01 SEG04-SEG14."""
import subprocess, json, os, time

ARK_API_KEY = "973a9b4b-2975-4e57-ae08-4c18fd2e2f58"
PROJECT_ROOT = "/Users/lei/Movies/demo1/dramas/前任的弟弟是我的租客"
SCRIPT = "/Users/lei/Movies/demo1/mcps/volc-ark/scripts/ark_seedance_video.py"
OUTDIR = os.path.join(PROJECT_ROOT, "assets/generated/EP01")

tasks = [
    ("SEG04", "cgt-20260609180741-tjkh9"),
    ("SEG05", "cgt-20260609180750-gfrbf"),
    ("SEG06", "cgt-20260609180758-rcn98"),
    ("SEG07", "cgt-20260609180804-85d6l"),
    ("SEG08", "cgt-20260609180811-8vx9b"),
    ("SEG09", "cgt-20260609180819-tfw76"),
    ("SEG10", "cgt-20260609180827-cfhdz"),
    ("SEG11", "cgt-20260609180835-6n8fn"),
    ("SEG12", "cgt-20260609180844-hz8qp"),
    ("SEG13", "cgt-20260609180852-w8lcs"),
    ("SEG14", "cgt-20260609180900-8ktmc"),
]

env = os.environ.copy()
env["ARK_API_KEY"] = ARK_API_KEY
env["DRAMA_PROJECT_ROOT"] = PROJECT_ROOT

MAX_WAIT = 600  # 10 min max
pending = tasks[:]
completed = []

start = time.time()
while pending and (time.time() - start) < MAX_WAIT:
    still_pending = []
    for seg_id, tid in pending:
        r = subprocess.run(
            ["python3", SCRIPT, "get", "--task-id", tid],
            env=env, capture_output=True, text=True, timeout=30
        )
        try:
            d = json.loads(r.stdout)
            status = d.get("status", "?")
        except:
            print(f"  {seg_id}: parse error: {r.stdout[:80]}")
            still_pending.append((seg_id, tid))
            continue

        if status == "succeeded":
            # Download
            out_path = os.path.join(OUTDIR, f"EP01_{seg_id}.mp4")
            r2 = subprocess.run(
                ["python3", SCRIPT, "download", "--task-id", tid, "--output", out_path],
                env=env, capture_output=True, text=True, timeout=60
            )
            try:
                d2 = json.loads(r2.stdout)
                print(f"  ✅ {seg_id}: {out_path} ({d2.get('bytes',0)//1024}KB)")
            except:
                print(f"  ⚠️ {seg_id}: download output: {r2.stdout[:100]}")
            completed.append(seg_id)
        elif status in ("failed", "cancelled"):
            print(f"  ❌ {seg_id}: {status}")
            completed.append(seg_id)
        else:
            still_pending.append((seg_id, tid))

    pending = still_pending
    if pending:
        remaining = [s for s, _ in pending]
        print(f"  ⏳ Waiting: {remaining} ({time.time()-start:.0f}s)")
        time.sleep(15)

if pending:
    print(f"\n⚠️ Timeout with {len(pending)} pending: {[s for s,_ in pending]}")
else:
    print(f"\n🎉 All {len(completed)} segments completed in {time.time()-start:.0f}s!")
