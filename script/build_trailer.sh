#!/usr/bin/env bash
# 《错嫁后我改写了王朝》60 秒概念预告：静图拼接为 1920x1080 MP4
# 依赖：ffmpeg（macOS: brew install ffmpeg）

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/video/output"
TMP="$OUT/tmp_segments"
SEG_DUR=5

command -v ffmpeg >/dev/null 2>&1 || {
  echo "未找到 ffmpeg。请先安装: brew install ffmpeg" >&2
  exit 1
}

mkdir -p "$TMP" "$OUT"

# 与「概念预告_60秒_脚本.md」顺序一致
IMGS=(
  "$ROOT/scene-concepts/scene-suwangfu-gate.png"
  "$ROOT/character-concepts/char-shen-zhiwei-wangfei.png"
  "$ROOT/scene-concepts/scene-dahun-bridal-chamber.png"
  "$ROOT/character-concepts/char-xiao-chengyuan-suwang.png"
  "$ROOT/scene-concepts/scene-fengyi-palace.png"
  "$ROOT/character-concepts/char-xiao-jingheng-taizi.png"
  "$ROOT/scene-concepts/scene-donggong-feast-hall.png"
  "$ROOT/character-concepts/char-huanghou.png"
  "$ROOT/scene-concepts/scene-gongmen-standoff.png"
  "$ROOT/scene-concepts/scene-dachao-hall.png"
  "$ROOT/scene-concepts/scene-xingchang-platform.png"
  "$ROOT/scene-concepts/scene-suwangfu-gate.png"
)

SCALE="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p"

i=0
for img in "${IMGS[@]}"; do
  if [[ ! -f "$img" ]]; then
    echo "缺少图片: $img" >&2
    exit 1
  fi
  part="$TMP/part$(printf '%03d' "$i").mp4"
  ffmpeg -y -hide_banner -loglevel error \
    -loop 1 -t "$SEG_DUR" -i "$img" \
    -vf "$SCALE" -c:v libx264 -pix_fmt yuv420p -r 30 \
    "$part"
  i=$((i + 1))
done

LIST="$OUT/concat_list.txt"
: > "$LIST"
shopt -s nullglob
for f in "$TMP"/part*.mp4; do
  printf "file '%s'\n" "$f" >> "$LIST"
done
shopt -u nullglob

RAW="$OUT/trailer_60s_nosub.mp4"
ffmpeg -y -hide_banner -loglevel error \
  -f concat -safe 0 -i "$LIST" -c copy "$RAW"

echo "已生成: $RAW"
echo "如需烧录字幕（需本机字体，可能需改字体路径）："
echo "  ffmpeg -y -i \"$RAW\" -vf \"subtitles='$ROOT/video/trailer_subtitles.srt':force_style='FontName=PingFang SC,FontSize=24,Outline=2'\" -c:a copy \"$OUT/trailer_60s_subbed.mp4\""
echo "更省事：用剪映导入成片 + trailer_subtitles.srt 对齐微调。"
