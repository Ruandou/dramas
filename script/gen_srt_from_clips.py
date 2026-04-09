#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据「成片顺序」的 MP4 列表，用 ffprobe 读每段时长，累加生成 SRT。
对白行与片段一一对应；空字符串表示该镜不出字。

用法（在仓库根）：
  python3 video/automation/gen_srt_from_clips.py \\
    --clips video/automation/ep01_clip_list.txt \\
    --lines video/automation/ep01_lines.txt \\
    --out video/第01集_即梦14镜_对白参考.srt
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def ffprobe_duration(path: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(r.stdout.strip())


def fmt_srt_time(sec: float) -> str:
    if sec < 0:
        sec = 0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    whole = int(s)
    ms = int(round((s - whole) * 1000))
    if ms >= 1000:
        whole += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{whole:02d},{ms:03d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True, help="UTF-8，每行一条相对仓库根的 MP4")
    ap.add_argument("--lines", required=True, help="UTF-8，每行一条字幕；空行=该镜不出字")
    ap.add_argument("--out", required=True, help="输出 .srt 相对仓库根")
    args = ap.parse_args()
    root = repo_root()

    clip_paths = []
    for line in (root / args.clips).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        clip_paths.append(root / line)

    line_texts = []
    for line in (root / args.lines).read_text(encoding="utf-8").splitlines():
        line_texts.append(line.rstrip("\n"))

    if len(line_texts) < len(clip_paths):
        print("对白行数少于片段数，将用空行补足", file=sys.stderr)
        line_texts.extend([""] * (len(clip_paths) - len(line_texts)))
    elif len(line_texts) > len(clip_paths):
        line_texts = line_texts[: len(clip_paths)]

    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    t = 0.0
    idx = 0
    blocks = []
    for clip, text in zip(clip_paths, line_texts):
        if not clip.is_file():
            raise FileNotFoundError(clip)
        d = ffprobe_duration(clip)
        t0, t1 = t, t + d
        t = t1
        text = text.strip()
        if not text:
            continue
        idx += 1
        blocks.append(
            f"{idx}\n{fmt_srt_time(t0)} --> {fmt_srt_time(t1)}\n{text}\n"
        )

    out_path.write_text("\n".join(blocks) + ("\n" if blocks else ""), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
