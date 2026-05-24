#!/usr/bin/env bash
# Burn SRT onto video using EP04 libass style (white text, black outline, no bar).
set -euo pipefail

SRC="${1:?source mp4}"
SRT="${2:?srt file}"
DST="${3:?output mp4}"

FFMPEG="${FFMPEG:-}"
if [[ -z "$FFMPEG" ]]; then
  for p in /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg /usr/local/opt/ffmpeg-full/bin/ffmpeg; do
    if [[ -x "$p" ]]; then FFMPEG="$p"; break; fi
  done
fi
FFMPEG="${FFMPEG:-ffmpeg}"

if ! "$FFMPEG" -hide_banner -filters 2>&1 | grep -q ' subtitles '; then
  echo "ERROR: ffmpeg lacks libass subtitles filter. Install: brew install ffmpeg-full" >&2
  exit 1
fi

ESC=$(python3 - "$SRT" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]).resolve()
print(str(p).replace("\\", "/").replace(":", r"\:").replace("'", r"\'"))
PY
)

STYLE="FontName=PingFang SC,FontSize=16,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Alignment=2,MarginV=35"
VF="subtitles=${ESC}:charenc=UTF-8:force_style='${STYLE}'"

exec "$FFMPEG" -y -i "$SRC" -vf "$VF" -c:a copy -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p "$DST"
