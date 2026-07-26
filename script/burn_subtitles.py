#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 EP##_segments.yaml 提取对白，生成 SRT 并烧录字幕、拼接成片。

本机 ffmpeg 无 libass/subtitles/drawtext 滤镜（Homebrew 精简构建），
故用 PIL 渲染字幕条 PNG + overlay enable=between(t,..) 烧录。

对白时间轴为估算：每段内按台词字数比例分配（无 ASR 对齐），
排版为底部居中白字黑边，超长自动折行。

用法（仓库根）：
  python3 script/burn_subtitles.py EP01 --project-root dramas/<剧名>
产出：
  <project>/剧本/EP01/EP01_对白.srt          （字幕文件）
  <project>/assets/generated/EP01/EP01_成片.mp4      （无字幕拼接）
  <project>/assets/generated/EP01/EP01_成片_字幕.mp4 （烧录字幕成片）
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]
FONT_SIZE = 40
WRAP_CHARS = 15          # 每行最大字符数
BOTTOM_MARGIN = 96       # 字幕底边距画面底部
LEAD_IN = 0.5            # 每段首条台词起始偏移
TAIL_PAD = 0.4           # 每段末尾留白
MIN_CUE = 1.0            # 单条最短显示时长

DIALOG_RE = re.compile(r"对白（([^，）]+)[^）]*）：「(.+?)」", re.S)


def ffprobe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def fmt_srt(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def load_font() -> ImageFont.FreeTypeFont:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, FONT_SIZE)
    print("未找到中文字体", file=sys.stderr)
    sys.exit(1)


def wrap(text: str, n: int) -> list[str]:
    return [text[i:i + n] for i in range(0, len(text), n)] or [text]


def render_cue_png(text: str, width: int, out: Path, font) -> int:
    """渲染透明底字幕条，返回图高。"""
    lines = wrap(text, WRAP_CHARS)
    line_h = FONT_SIZE + 14
    h = line_h * len(lines) + 12
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=font)
        x = (width - w) / 2
        y = 6 + i * line_h
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=3, stroke_fill=(0, 0, 0, 220))
    img.save(out)
    return h


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--no-burn", action="store_true", help="只出 SRT 和拼接，不烧字幕")
    args = ap.parse_args()

    ep = args.episode
    proj = Path(args.project_root)
    seg_yaml = proj / "剧本" / ep / f"{ep}_segments.yaml"
    gen_dir = proj / "assets" / "generated" / ep
    data = yaml.safe_load(seg_yaml.read_text(encoding="utf-8"))
    segments = data.get("segments") or data.get("Segments")

    # 1. 收集片段与对白，累加时间轴
    cues = []  # (start, end, text)
    clips = []
    t0 = 0.0
    for seg in segments:
        sid = seg["segment_id"]
        mp4 = gen_dir / f"{sid}.mp4"
        if not mp4.is_file():
            print(f"缺片段视频：{mp4}", file=sys.stderr)
            sys.exit(1)
        dur = ffprobe_duration(mp4)
        clips.append((mp4, dur))
        lines = [m[1].strip() for m in DIALOG_RE.findall(seg["api"]["text"])]
        if lines:
            usable = max(dur - LEAD_IN - TAIL_PAD, MIN_CUE * len(lines))
            weights = [max(len(x), 4) for x in lines]
            total_w = sum(weights)
            t = t0 + LEAD_IN
            for ln, w in zip(lines, weights):
                d = max(usable * w / total_w, MIN_CUE)
                end = min(t + d, t0 + dur - 0.1)
                cues.append((t, end, ln))
                t = end
        t0 += dur

    # 2. 写 SRT
    srt_path = seg_yaml.parent / f"{ep}_对白.srt"
    with srt_path.open("w", encoding="utf-8") as f:
        for i, (s, e, txt) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{txt}\n\n")
    print(f"SRT: {srt_path}  cues={len(cues)}  总时长={t0:.2f}s")

    # 3. 拼接（统一音频采样率）
    raw = gen_dir / f"{ep}_成片.mp4"
    n = len(clips)
    inputs = []
    for mp4, _ in clips:
        inputs += ["-i", str(mp4)]
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-r", "24", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-b:a", "128k",
         str(raw)], check=True)
    print(f"拼接完成: {raw}")
    if args.no_burn:
        return

    # 4. 渲染字幕 PNG + overlay 烧录
    width, height = 720, 1280
    subs_dir = gen_dir / "_subs"
    subs_dir.mkdir(exist_ok=True)
    font = load_font()
    over_inputs, chain = [], []
    prev = "0:v"
    for i, (s, e, txt) in enumerate(cues):
        png = subs_dir / f"cue{i:03d}.png"
        h = render_cue_png(txt, width, png, font)
        over_inputs += ["-i", str(png)]
        y = height - BOTTOM_MARGIN - h
        out = f"v{i}"
        chain.append(
            f"[{prev}][{i + 1}:v]overlay=0:{y}:enable='between(t,{s:.3f},{e:.3f})'[{out}]")
        prev = out
    final = gen_dir / f"{ep}_成片_字幕.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), *over_inputs,
         "-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-map", "0:a",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", str(final)], check=True)
    print(f"烧录完成: {final}")


if __name__ == "__main__":
    main()
