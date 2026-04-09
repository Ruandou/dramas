#!/usr/bin/env bash
# 第1集第1镜（场1-1A 大全景）— 文生视频提交示例
# 用法：在终端先 export VOLC_ACCESS_KEY 与 VOLC_SECRET_KEY，再执行：
#   bash mcp/volc-jimeng/scripts/run_ep01_lens1.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -z "${VOLC_ACCESS_KEY:-}" ]] || [[ -z "${VOLC_SECRET_KEY:-}" ]]; then
  echo "请先设置环境变量: VOLC_ACCESS_KEY 与 VOLC_SECRET_KEY" >&2
  exit 1
fi
python3 - "$SCRIPT_DIR" << 'PY'
import json, subprocess, sys, os
script_dir = sys.argv[1]
prompt = (
    "古风将军府后院，白日，红绸喜字，家丁穿行，电影感竖屏9比16，写实，略阴郁色调，"
    "固定镜头缓慢推进，无现代物品，无字幕"
)
payload = {
    "action": "CVSync2AsyncSubmitTask",
    "version": "2022-08-31",
    "body": {
        "req_key": "jimeng_ti2v_v30_pro",
        "prompt": prompt,
        "aspect_ratio": "9:16",
    },
}
script = os.path.join(script_dir, "volc_visual_submit.py")
p = subprocess.run(
    [sys.executable, script],
    input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    capture_output=True,
    cwd=script_dir,
)
sys.stdout.buffer.write(p.stdout)
sys.stderr.buffer.write(p.stderr)
sys.exit(p.returncode)
PY
