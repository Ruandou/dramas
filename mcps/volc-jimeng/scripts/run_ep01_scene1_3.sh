#!/usr/bin/env bash
# 第1集 场1-3（新房 · 夜 · 内）四镜 1-3A～1-3D — 文生视频依次提交
# 用法：export VOLC_ACCESS_KEY VOLC_SECRET_KEY 后
#   bash mcp/volc-jimeng/scripts/run_ep01_scene1_3.sh
# 镜号对应本地命名建议：第11～14镜_场1-3A～D（与场1-1/1-2衔接）
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -z "${VOLC_ACCESS_KEY:-}" ]] || [[ -z "${VOLC_SECRET_KEY:-}" ]]; then
  echo "请先设置环境变量: VOLC_ACCESS_KEY 与 VOLC_SECRET_KEY" >&2
  exit 1
fi
python3 - "$SCRIPT_DIR" << 'PY'
import json, subprocess, sys, os, time

script_dir = sys.argv[1]
script = os.path.join(script_dir, "volc_visual_submit.py")

shots = [
    ("1-3A", "古风喜房，红烛高照，新娘独自掀盖头环顾，门窗紧闭，静谧诡异，架空古风，电影感竖屏9比16，写实，夜晚室内，中景，无现代物品无字幕"),
    ("1-3B", "手推门不动，门闩特写，轻微震动，红烛光，架空古风喜房，电影感竖屏9比16，写实，夜晚，特写，无现代物品无字幕"),
    ("1-3C", "窗纸剪影人影一闪而过，新娘后退半步，惊恐克制，架空古风喜房夜晚，红烛，电影感竖屏9比16，写实，中景，无现代物品无字幕"),
    ("1-3D", "烛火猛晃，阴影扫过喜床，架空古风喜房夜晚，悬疑氛围，电影感竖屏9比16，写实，无现代物品无字幕"),
]

for i, (label, prompt) in enumerate(shots):
    if i > 0:
        time.sleep(8)
    payload = {
        "action": "CVSync2AsyncSubmitTask",
        "version": "2022-08-31",
        "body": {
            "req_key": "jimeng_ti2v_v30_pro",
            "prompt": prompt,
            "aspect_ratio": "9:16",
        },
    }
    print(f"--- 提交 {label} ---", flush=True)
    p = subprocess.run(
        [sys.executable, script],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        cwd=script_dir,
    )
    sys.stdout.buffer.write(p.stdout)
    sys.stdout.buffer.write(b"\n")
    if p.stderr:
        sys.stderr.buffer.write(p.stderr)
    if p.returncode != 0:
        sys.exit(p.returncode)
PY
