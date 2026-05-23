#!/usr/bin/env bash
# 按 EP##_segments.yaml 顺序无重编码拼接段落 mp4
set -euo pipefail
EP="${1:?用法: ffmpeg_concat_episode.sh EP01}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SEG_YAML="$ROOT/剧本/${EP}_segments.yaml"
OUT_DIR="$ROOT/assets/generated/${EP}"
OUT_MP4="$OUT_DIR/${EP}_full.mp4"
LIST="$OUT_DIR/concat_list.txt"

if [[ ! -f "$SEG_YAML" ]]; then
  echo "缺少 $SEG_YAML" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
: >"$LIST"

python3 - "$SEG_YAML" "$OUT_DIR" "$LIST" <<'PY'
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("需要 PyYAML: pip3 install pyyaml")

seg_yaml, out_dir, list_path = sys.argv[1:4]
doc = yaml.safe_load(Path(seg_yaml).read_text(encoding="utf-8"))
out = Path(out_dir)
lines = []
for seg in doc.get("segments") or []:
    sid = seg.get("segment_id")
    if not sid:
        continue
    mp4 = out / f"{sid}.mp4"
    if not mp4.is_file():
        print(f"缺少 {mp4}", file=sys.stderr)
        sys.exit(1)
    lines.append(f"file '{mp4.resolve()}'")
Path(list_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {len(lines)} entries to {list_path}")
PY

FFMPEG="${FFMPEG:-ffmpeg}"
if ! command -v "$FFMPEG" >/dev/null 2>&1; then
  echo "未找到 ffmpeg。已生成 $LIST，安装后执行：" >&2
  echo "  ffmpeg -y -f concat -safe 0 -i \"$LIST\" -c copy \"$OUT_MP4\"" >&2
  exit 2
fi
"$FFMPEG" -y -f concat -safe 0 -i "$LIST" -c copy "$OUT_MP4"
echo "→ $OUT_MP4"
ls -lh "$OUT_MP4"
