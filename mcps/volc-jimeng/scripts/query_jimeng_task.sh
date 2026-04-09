#!/usr/bin/env bash
# 查询即梦异步任务（CVSync2AsyncGetResult）
# 用法：export VOLC_ACCESS_KEY VOLC_SECRET_KEY 后
#   bash mcp/volc-jimeng/scripts/query_jimeng_task.sh <task_id> [req_key]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TASK_ID="${1:-}"
REQ_KEY="${2:-jimeng_ti2v_v30_pro}"
if [[ -z "${VOLC_ACCESS_KEY:-}" ]] || [[ -z "${VOLC_SECRET_KEY:-}" ]]; then
  echo "请先设置环境变量: VOLC_ACCESS_KEY 与 VOLC_SECRET_KEY" >&2
  exit 1
fi
if [[ -z "$TASK_ID" ]]; then
  echo "用法: $0 <task_id> [req_key]" >&2
  exit 1
fi
python3 - "$SCRIPT_DIR" "$TASK_ID" "$REQ_KEY" << 'PY'
import json, subprocess, sys, os
script_dir, task_id, req_key = sys.argv[1], sys.argv[2], sys.argv[3]
payload = {
    "action": "CVSync2AsyncGetResult",
    "version": "2022-08-31",
    "body": {"req_key": req_key, "task_id": task_id},
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
