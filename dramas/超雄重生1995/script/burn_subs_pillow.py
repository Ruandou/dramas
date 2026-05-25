#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Burn SRT into MP4 via Pillow PNG overlays + ffmpeg filter_complex.
Style matches EP04: white text, black outline, bottom center, no background bar.
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def load_local_pipeline():
    lp_path = Path(__file__).resolve().parents[3] / "script" / "local_pipeline.py"
    spec = importlib.util.spec_from_file_location("local_pipeline", lp_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render_subtitle_pngs_ep04_style(
    cues: list[tuple[float, float, str]],
    size: tuple[int, int],
    font_path: Path,
    tmpdir: Path,
) -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont

    w, h = size
    margin_bottom = max(28, h // 36)  # ~MarginV=35 on 1280p
    font_size = max(22, min(34, h // 38))  # EP04 libass FontSize≈16 feel
    try:
        font = ImageFont.truetype(str(font_path), font_size, index=0)
    except OSError:
        font = ImageFont.truetype(str(font_path), font_size, index=1)

    outline = 2
    line_gap = 4
    paths: list[Path] = []
    approx_char_w = max(font_size // 2, 12)
    max_line_chars = max(10, w // approx_char_w)

    for i, (_t0, _t1, text) in enumerate(cues):
        lines: list[str] = []
        for para in text.splitlines():
            wrapped = textwrap.wrap(para, width=max_line_chars) or ([para] if para else [""])
            lines.extend(wrapped)
        if not lines:
            lines = [""]

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        line_heights: list[int] = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])

        block_h = sum(line_heights) + line_gap * (len(lines) - 1)
        y = h - margin_bottom - block_h

        for line, lh in zip(lines, line_heights):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (w - tw) // 2
            for dx in range(-outline, outline + 1):
                for dy in range(-outline, outline + 1):
                    if dx == 0 and dy == 0:
                        continue
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            y += lh + line_gap

        outp = tmpdir / f"sub_{i:04d}.png"
        img.save(outp, "PNG")
        paths.append(outp)

    return paths


def burn_pillow(
    lp,
    src: Path,
    srt: Path,
    dst: Path,
    *,
    font_path: Path | None = None,
) -> None:
    root = src.parents[2]  # assets/generated/EPxx
    project_root = root.parent.parent
    font = font_path or lp.default_cjk_font(project_root, None)
    cues = lp.parse_srt(srt)
    if not cues:
        shutil.copy2(src, dst)
        print(f"No cues in {srt}, copied source → {dst}")
        return

    ffmpeg = lp.pick_ffmpeg()
    ffprobe = lp.pick_ffprobe()
    duration = lp.ffprobe_duration(src, ffprobe)
    w, h = lp.ffprobe_video_size(src, ffprobe)
    has_a = lp.ffprobe_has_audio(src, ffprobe)

    print(f"Burning {len(cues)} cues ({w}x{h}, font={font.name})…")

    with tempfile.TemporaryDirectory(prefix="subburn_") as td:
        tdir = Path(td)
        pngs = render_subtitle_pngs_ep04_style(cues, (w, h), font, tdir)

        parts: list[str] = []
        prev = "[0:v]"
        for i, ((t0, t1, _txt), _png) in enumerate(zip(cues, pngs)):
            n = i + 1
            tag = f"v{n}"
            parts.append(
                f"{prev}[{n}:v]overlay=0:0:format=auto:"
                f"enable='between(t\\,{t0}\\,{t1})'[{tag}]"
            )
            prev = f"[{tag}]"
        fc = ";".join(parts)
        last = f"v{len(cues)}"

        cmd = [ffmpeg, "-y", "-i", str(src)]
        for png in pngs:
            cmd += [
                "-loop", "1", "-framerate", "25",
                "-t", f"{duration:.3f}", "-i", str(png),
            ]
        cmd += ["-filter_complex", fc, "-map", f"[{last}]"]
        if has_a:
            cmd += ["-map", "0:a", "-c:a", "copy"]
        cmd += [
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", str(dst),
        ]
        subprocess.run(cmd, check=True)

    print(f"Done → {dst} ({dst.stat().st_size // 1024 // 1024} MB)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Burn SRT (EP04 Pillow style)")
    parser.add_argument("video", type=Path, help="Source MP4")
    parser.add_argument("srt", type=Path, help="SRT file")
    parser.add_argument("-o", "--output", type=Path, help="Output MP4")
    args = parser.parse_args()

    src = args.video.resolve()
    srt = args.srt.resolve()
    dst = (args.output or src.with_name(src.stem + "_subtitled.mp4")).resolve()

    if not src.is_file():
        print(f"ERROR: video not found: {src}", file=sys.stderr)
        return 1
    if not srt.is_file():
        print(f"ERROR: srt not found: {srt}", file=sys.stderr)
        return 1

    lp = load_local_pipeline()
    burn_pillow(lp, src, srt, dst)
    sidecar = dst.with_suffix(".srt")
    shutil.copy2(srt, sidecar)
    print(f"Sidecar → {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
