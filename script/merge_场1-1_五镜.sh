#!/usr/bin/env bash
# 将场 1-1 已下载的 5 段即梦成片按镜号顺序无损拼接（依赖 ffmpeg）
# 用法：bash video/merge_场1-1_五镜.sh
# macOS 未安装时：brew install ffmpeg

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEN="$ROOT/video/generated"
OUT="$ROOT/video/output"
mkdir -p "$OUT"

command -v ffmpeg >/dev/null 2>&1 || {
  echo "未找到 ffmpeg。安装: brew install ffmpeg" >&2
  exit 1
}

FILES=(
  "第01镜_场1-1A_jimeng.mp4"
  "第02镜_场1-1B_jimeng.mp4"
  "第03镜_场1-1C_jimeng.mp4"
  "第04镜_场1-1D_jimeng.mp4"
  "第05镜_场1-1E_jimeng.mp4"
)

for f in "${FILES[@]}"; do
  if [[ ! -f "$GEN/$f" ]]; then
    echo "缺少文件: $GEN/$f" >&2
    exit 1
  fi
done

LIST="$(mktemp)"
trap 'rm -f "$LIST"' EXIT

for f in "${FILES[@]}"; do
  printf "file '%s'\n" "$GEN/$f" >> "$LIST"
done

DEST="$OUT/第01集_场1-1_五镜连播.mp4"
echo "拼接 -> $DEST"
if ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy "$DEST" 2>/dev/null; then
  ls -la "$DEST"
  echo "完成（流复制 -c copy，无重编码）。"
  exit 0
fi

echo "流复制失败（编码/分辨率不一致时常见），改用重编码拼接…" >&2
ffmpeg -y -f concat -safe 0 -i "$LIST" \
  -c:v libx264 -preset fast -crf 20 -c:a aac -b:a 128k \
  "$DEST"
ls -la "$DEST"
echo "完成（已重编码）。"
