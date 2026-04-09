#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
零预算本地自动化：ffmpeg 拼接 + 可选 BGM 混音 + 可选 SRT（软轨 mov_text 或硬字幕烧录）。
依赖：系统已安装 ffmpeg/ffprobe（brew install ffmpeg）。硬字幕优先用带 libass 的 ffmpeg（brew install ffmpeg-full，
二进制通常在 /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg，可设环境变量 FFMPEG）；否则需 pip install Pillow，用 PNG+overlay 烧录。

用法（在仓库根 demo1 下）：
  python3 video/automation/local_pipeline.py --config video/automation/config_ep01.json
  python3 video/automation/local_pipeline.py --config video/automation/config_ep01.json --dry-run

可选：在 config 里填写 "bgm"、"srt"。
burn_subtitles（默认 true）：把字幕画进画面，任意播放器可见；false 时仅 mux mov_text 软轨（QuickTime 常不显示）。
silent_audio_if_missing（默认 true）：拼接后若无音轨则注入一条 AAC 音轨。
noise_bed_if_no_bgm（默认 false）：未配置 bgm 时用极低粉/棕噪声作底噪（可听见）；否则用纯静音 anullsrc。
要正常配乐请在 config 里填写 bgm 路径。
sidecar_srt（默认 true）：成片旁路复制同名 .srt，便于播放器自动加载。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def run(
    cmd: list[str], *, cwd: str | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, cwd=cwd)


def ffprobe_has_audio(path: Path, ffprobe: str | None = None) -> bool:
    exe = ffprobe or shutil.which("ffprobe") or "ffprobe"
    r = subprocess.run(
        [
            exe,
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    return bool(r.stdout.strip())


def pick_ffmpeg() -> str:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    for p in (
        "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
        "/usr/local/opt/ffmpeg-full/bin/ffmpeg",
    ):
        if Path(p).is_file():
            return str(p)
    return shutil.which("ffmpeg") or "ffmpeg"


def pick_ffprobe() -> str:
    if os.environ.get("FFPROBE"):
        return os.environ["FFPROBE"]
    for p in (
        "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe",
        "/usr/local/opt/ffmpeg-full/bin/ffprobe",
    ):
        if Path(p).is_file():
            return str(p)
    return shutil.which("ffprobe") or "ffprobe"


def ffmpeg_list_filters(ffmpeg_exe: str) -> str:
    r = subprocess.run(
        [ffmpeg_exe, "-hide_banner", "-filters"],
        capture_output=True,
        text=True,
    )
    return r.stdout


def ffmpeg_has_subtitles_filter(ffmpeg_exe: str) -> bool:
    for line in ffmpeg_list_filters(ffmpeg_exe).splitlines():
        if "subtitles" in line and "V->V" in line:
            return True
    return False


def ffprobe_duration(path: Path, ffprobe: str | None = None) -> float:
    exe = ffprobe or shutil.which("ffprobe") or "ffprobe"
    r = subprocess.run(
        [
            exe,
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


def ffprobe_video_size(path: Path, ffprobe: str | None = None) -> tuple[int, int]:
    exe = ffprobe or shutil.which("ffprobe") or "ffprobe"
    r = subprocess.run(
        [
            exe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    w, h = r.stdout.strip().split(",")
    return int(w), int(h)


def escape_subtitles_path(path: Path) -> str:
    s = str(path.resolve()).replace("\\", "/")
    return s.replace(":", r"\:").replace("'", r"\'")


def _ts_to_sec(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    raw = path.read_text(encoding="utf-8-sig").strip()
    if not raw:
        return []
    cues: list[tuple[float, float, str]] = []
    for block in re.split(r"\n\s*\n+", raw):
        lines = [ln.rstrip() for ln in block.splitlines()]
        lines = [ln for ln in lines if ln.strip() != ""]
        if len(lines) < 2:
            continue
        i = 0
        if re.match(r"^\d+\s*$", lines[0].strip()):
            i = 1
        if i >= len(lines):
            continue
        m = re.match(
            r"(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d\d):(\d\d):(\d\d)[,.](\d{3})",
            lines[i].strip(),
        )
        if not m:
            continue
        t0 = _ts_to_sec(m.group(1), m.group(2), m.group(3), m.group(4))
        t1 = _ts_to_sec(m.group(5), m.group(6), m.group(7), m.group(8))
        text = "\n".join(lines[i + 1 :]).strip()
        if text:
            cues.append((t0, t1, text))
    return cues


def default_cjk_font(root: Path, cfg_font: str | None) -> Path:
    if cfg_font:
        p = (root / cfg_font).resolve()
        if p.is_file():
            return p
        raise FileNotFoundError(f"subtitle_font 不存在: {p}")
    for p in (
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
    ):
        if p.is_file():
            return p
    raise FileNotFoundError(
        "未找到中文字体。请在 config 里设置 subtitle_font（.ttf/.ttc 路径）。"
    )


def render_subtitle_pngs(
    cues: list[tuple[float, float, str]],
    size: tuple[int, int],
    font_path: Path,
    tmpdir: Path,
) -> list[Path]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as e:
        raise RuntimeError(
            "当前 ffmpeg 无 libass subtitles 滤镜，硬字幕需：brew install ffmpeg-full，或 pip install Pillow"
        ) from e

    w, h = size
    margin = max(24, h // 40)
    font_size = max(28, min(52, h // 22))
    try:
        font = ImageFont.truetype(str(font_path), font_size, index=0)
    except OSError:
        font = ImageFont.truetype(str(font_path), font_size, index=1)

    paths: list[Path] = []
    approx_char_w = max(font_size // 2, 14)
    max_line_chars = max(8, w // approx_char_w)

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
        line_gap = 8
        block_h = sum(line_heights) + line_gap * (len(lines) - 1)
        pad_y = 18
        box_top = h - margin - block_h - 2 * pad_y
        box_bottom = h - margin
        draw.rectangle(
            (margin, box_top, w - margin, box_bottom),
            fill=(0, 0, 0, 165),
        )

        y = box_top + pad_y
        for line, lh in zip(lines, line_heights):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (w - tw) // 2
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 220))
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            y += lh + line_gap

        outp = tmpdir / f"sub_{i:04d}.png"
        img.save(outp, "PNG")
        paths.append(outp)

    return paths


def burn_subtitles_libass(
    ffmpeg_exe: str,
    ffprobe_exe: str,
    src: Path,
    srt_path: Path,
    dst: Path,
    *,
    dry_run: bool,
) -> None:
    vf = f"subtitles={escape_subtitles_path(srt_path)}:charenc=UTF-8"
    has_a = ffprobe_has_audio(src, ffprobe_exe)
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(src),
        "-vf",
        vf,
        "-map",
        "0:v",
    ]
    if has_a:
        cmd += ["-map", "0:a", "-c:a", "copy"]
    cmd += [
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        str(dst),
    ]
    if dry_run:
        print(" ".join(cmd))
        return
    run(cmd)


def burn_subtitles_pillow_overlay(
    ffmpeg_exe: str,
    ffprobe_exe: str,
    src: Path,
    cues: list[tuple[float, float, str]],
    dst: Path,
    font_path: Path,
    *,
    dry_run: bool,
) -> None:
    if not cues:
        shutil.copy2(src, dst)
        return

    duration = ffprobe_duration(src, ffprobe_exe)
    w, h = ffprobe_video_size(src, ffprobe_exe)
    has_a = ffprobe_has_audio(src, ffprobe_exe)

    with tempfile.TemporaryDirectory(prefix="subburn_") as td:
        tdir = Path(td)
        pngs = render_subtitle_pngs(cues, (w, h), font_path, tdir)

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

        cmd = [ffmpeg_exe, "-y", "-i", str(src)]
        for png in pngs:
            cmd += [
                "-loop",
                "1",
                "-framerate",
                "25",
                "-t",
                f"{duration:.3f}",
                "-i",
                str(png),
            ]
        cmd += [
            "-filter_complex",
            fc,
            "-map",
            f"[{last}]",
        ]
        if has_a:
            cmd += ["-map", "0:a", "-c:a", "copy"]
        cmd += [
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            str(dst),
        ]
        if dry_run:
            print(" ".join(cmd))
            return
        run(cmd)


def build_concat_list(roots: Path, rels: list[str], tmp_list: Path) -> None:
    lines = []
    for rel in rels:
        p = (roots / rel).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"缺少片段: {p}")
        esc = str(p).replace("'", "'\\''")
        lines.append(f"file '{esc}'")
    tmp_list.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="本地 ffmpeg 成片流水线")
    ap.add_argument("--config", required=True, help="JSON 配置路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印将要执行的命令")
    args = ap.parse_args()

    root = repo_root()
    cfg_path = (root / args.config).resolve() if not os.path.isabs(args.config) else Path(args.config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    clips = cfg["clips"]
    out_rel = cfg["output"]
    bgm_rel = cfg.get("bgm")
    bgm_vol = float(cfg.get("bgm_volume", 0.22))
    srt_rel = cfg.get("srt")
    silent_if_no_audio = bool(cfg.get("silent_audio_if_missing", True))
    noise_bed_if_no_bgm = bool(cfg.get("noise_bed_if_no_bgm", False))
    noise_bed_amplitude = float(cfg.get("noise_bed_amplitude", 0.08))
    sidecar_srt = bool(cfg.get("sidecar_srt", True))
    burn_subtitles = bool(cfg.get("burn_subtitles", True))
    subtitle_font_cfg = cfg.get("subtitle_font")

    ffmpeg_exe = pick_ffmpeg()
    ffprobe_exe = pick_ffprobe()

    out_path = (root / out_rel).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tmp:
        list_path = Path(tmp.name)
    try:
        build_concat_list(root, clips, list_path)
        merged = out_path.with_name(out_path.stem + "._merged_.mp4")

        cmd_merge = [
            ffmpeg_exe,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            str(merged),
        ]
        if args.dry_run:
            print(" ".join(cmd_merge))
            return

        run(cmd_merge)

        current = merged
        if bgm_rel:
            bgm_path = (root / bgm_rel).resolve()
            if not bgm_path.is_file():
                raise FileNotFoundError(f"BGM 不存在: {bgm_path}")
            mixed = out_path.with_name(out_path.stem + "._mixed_.mp4")
            has_a = ffprobe_has_audio(current, ffprobe_exe)
            if has_a:
                fc = (
                    f"[1:a]volume={bgm_vol}[bg];"
                    f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
                )
                cmd_mix = [
                    ffmpeg_exe,
                    "-y",
                    "-i",
                    str(current),
                    "-stream_loop",
                    "-1",
                    "-i",
                    str(bgm_path),
                    "-filter_complex",
                    fc,
                    "-map",
                    "0:v",
                    "-map",
                    "[aout]",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    str(mixed),
                ]
            else:
                cmd_mix = [
                    ffmpeg_exe,
                    "-y",
                    "-i",
                    str(current),
                    "-stream_loop",
                    "-1",
                    "-i",
                    str(bgm_path),
                    "-map",
                    "0:v",
                    "-map",
                    "1:a",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    str(mixed),
                ]
            run(cmd_mix)
            current.unlink(missing_ok=True)
            current = mixed

        if silent_if_no_audio and not ffprobe_has_audio(current, ffprobe_exe):
            withsilent = out_path.with_name(out_path.stem + "._withsilent_.mp4")
            if noise_bed_if_no_bgm and not bgm_rel:
                lavfi_in = (
                    f"anoisesrc=sample_rate=48000:color=brown:"
                    f"amplitude={noise_bed_amplitude}"
                )
            else:
                lavfi_in = "anullsrc=channel_layout=stereo:sample_rate=48000"
            cmd_pad = [
                ffmpeg_exe,
                "-y",
                "-i",
                str(current),
                "-f",
                "lavfi",
                "-i",
                lavfi_in,
                "-map",
                "0:v",
                "-map",
                "1:a",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                str(withsilent),
            ]
            run(cmd_pad)
            if current != out_path and current.is_file():
                current.unlink(missing_ok=True)
            current = withsilent

        if srt_rel:
            srt_path = (root / srt_rel).resolve()
            if not srt_path.is_file():
                raise FileNotFoundError(f"字幕不存在: {srt_path}")
            cues = parse_srt(srt_path)

            if burn_subtitles:
                font_path = default_cjk_font(root, subtitle_font_cfg)
                if ffmpeg_has_subtitles_filter(ffmpeg_exe):
                    burn_subtitles_libass(
                        ffmpeg_exe,
                        ffprobe_exe,
                        current,
                        srt_path,
                        out_path,
                        dry_run=False,
                    )
                else:
                    burn_subtitles_pillow_overlay(
                        ffmpeg_exe,
                        ffprobe_exe,
                        current,
                        cues,
                        out_path,
                        font_path,
                        dry_run=False,
                    )
                if current.is_file() and current.resolve() != out_path.resolve():
                    current.unlink(missing_ok=True)
            else:
                # mov_text 软轨；有音轨时一并 copy（静音/BGM），避免成片只有视频轨
                has_a = ffprobe_has_audio(current, ffprobe_exe)
                if has_a:
                    cmd_sub = [
                        ffmpeg_exe,
                        "-y",
                        "-i",
                        str(current),
                        "-f",
                        "srt",
                        "-i",
                        str(srt_path),
                        "-map",
                        "0:v",
                        "-map",
                        "0:a",
                        "-map",
                        "1",
                        "-c:v",
                        "copy",
                        "-c:a",
                        "copy",
                        "-c:s",
                        "mov_text",
                        str(out_path),
                    ]
                else:
                    cmd_sub = [
                        ffmpeg_exe,
                        "-y",
                        "-i",
                        str(current),
                        "-f",
                        "srt",
                        "-i",
                        str(srt_path),
                        "-map",
                        "0:v",
                        "-map",
                        "1",
                        "-c:v",
                        "copy",
                        "-c:s",
                        "mov_text",
                        str(out_path),
                    ]
                run(cmd_sub)
                if current.is_file() and current.resolve() != out_path.resolve():
                    current.unlink(missing_ok=True)

            if sidecar_srt:
                dest_srt = out_path.with_suffix(".srt")
                shutil.copy2(srt_path, dest_srt)
        else:
            if current != out_path:
                current.rename(out_path)

        print(json.dumps({"output": str(out_path)}, ensure_ascii=False, indent=2))
    finally:
        list_path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)
        sys.exit(e.returncode or 1)
