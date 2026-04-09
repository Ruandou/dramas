#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 tts_batch_edge 生成的「三位数字.mp3」按 SRT 每条字幕的起始时间叠到成片音轨上。
前提：SRT 与对白来自同一套 gen_srt_from_clips + ep01_lines；MP3 按行号命名（可跳号，如 002、005），
按数字升序排列后须与 SRT 中非空字幕条数、顺序一致。

用法（在仓库根）：
  python3 video/automation/mix_tts_from_srt.py \\
    --video video/output/第01集_全14镜_软字幕.mp4 \\
    --srt video/第01集_即梦14镜_对白参考.srt \\
    --tts-dir video/automation/tts_out \\
    --output video/output/第01集_带配音.mp4

可选：--original-volume 0.35（压低原片/环境音轨，默认 0.4）；成片无音轨时自动用静音底床。
可选：--bgm path/to/music.mp3 --bgm-volume 0.18（循环铺底，与对白、原片音轨一并 amix；实现「成片自带对白+背景乐」）。

说明：即梦 / MiniMax 文生视频接口通常只出画面，不保证返回带对白与配乐的音轨；要「下载即有声画」需本脚本或同类工具在本地/服务端混音。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check)


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


def ffprobe_has_audio(path: Path) -> bool:
    r = subprocess.run(
        [
            "ffprobe",
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


def srt_ts_to_sec(s: str) -> float:
    s = s.strip().replace(",", ".")
    parts = s.split(":")
    if len(parts) != 3:
        raise ValueError(f"非法 SRT 时间: {s!r}")
    h, m, sec = int(parts[0]), int(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + sec


def parse_srt_cues(content: str) -> list[tuple[float, float]]:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    cues: list[tuple[float, float]] = []
    for block in re.split(r"\n\s*\n", content.strip()):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        time_line = next((ln for ln in lines if "-->" in ln), None)
        if not time_line:
            continue
        m = re.search(
            r"(\d{1,2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{3})",
            time_line.strip(),
        )
        if not m:
            continue
        cues.append((srt_ts_to_sec(m.group(1)), srt_ts_to_sec(m.group(2))))
    return cues


def list_tts_mp3s(tts_dir: Path) -> list[Path]:
    files = [p for p in tts_dir.glob("*.mp3") if p.stem.isdigit()]
    files.sort(key=lambda p: int(p.stem))
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description="SRT 时间轴 + TTS mp3 混音到成片")
    ap.add_argument("--video", required=True, help="成片 MP4（相对仓库根或绝对路径）")
    ap.add_argument("--srt", required=True, help="与成片对齐的 UTF-8 SRT")
    ap.add_argument("--tts-dir", required=True, help="含 001.mp3 等（可跳号）的目录")
    ap.add_argument("--output", required=True, help="输出 MP4")
    ap.add_argument(
        "--original-volume",
        type=float,
        default=0.4,
        help="保留原片音轨时的音量系数 0～1，默认 0.4",
    )
    ap.add_argument(
        "--bgm",
        default=None,
        help="背景音乐文件（mp3/wav 等），将循环铺满成片时长后与对白混音",
    )
    ap.add_argument(
        "--bgm-volume",
        type=float,
        default=0.2,
        help="BGM 音量系数 0～1，默认 0.2",
    )
    ap.add_argument("--dry-run", action="store_true", help="只打印 ffmpeg 命令")
    args = ap.parse_args()

    root = repo_root()
    video = Path(args.video)
    if not video.is_file():
        video = root / args.video
    srt = Path(args.srt)
    if not srt.is_file():
        srt = root / args.srt
    tts_dir = Path(args.tts_dir)
    if not tts_dir.is_dir():
        tts_dir = root / args.tts_dir
    out = Path(args.output)
    if not out.is_absolute():
        out = (root / args.output).resolve()

    if not video.is_file():
        sys.exit(f"找不到视频: {video}")
    if not srt.is_file():
        sys.exit(f"找不到字幕: {srt}")
    if not tts_dir.is_dir():
        sys.exit(f"找不到 TTS 目录: {tts_dir}")

    bgm: Path | None = None
    if args.bgm:
        bgm = Path(args.bgm)
        if not bgm.is_file():
            bgm = root / args.bgm
        if not bgm.is_file():
            sys.exit(f"找不到 BGM 文件: {args.bgm}")

    cues = parse_srt_cues(srt.read_text(encoding="utf-8"))
    mp3s = list_tts_mp3s(tts_dir)
    if len(cues) != len(mp3s):
        sys.exit(
            f"SRT 字幕条数 ({len(cues)}) 与 TTS mp3 数量 ({len(mp3s)}) 不一致。"
            f"请确认与 gen_srt_from_clips / tts_batch_edge 使用同一套对白。"
        )

    dur = ffprobe_duration(video)
    has_a = ffprobe_has_audio(video)
    dstr = f"{dur:.6f}"

    parts: list[str] = []
    if has_a:
        parts.append(
            f"[0:a]aresample=48000,atrim=duration={dstr},asetpts=PTS-STARTPTS,"
            f"apad=whole_dur={dstr},volume={args.original_volume}[bed]"
        )
    else:
        parts.append(
            f"anullsrc=channel_layout=stereo:sample_rate=48000,"
            f"atrim=duration={dstr},asetpts=PTS-STARTPTS[bed]"
        )

    for i, ((t0, _t1), _mp3) in enumerate(zip(cues, mp3s)):
        inp = i + 1
        ms = max(0, int(round(t0 * 1000)))
        parts.append(
            f"[{inp}:a]aresample=48000,aformat=channel_layouts=stereo:sample_rates=48000,"
            f"adelay={ms}|{ms}[tts{i}]"
        )

    tts_labels = "".join(f"[tts{i}]" for i in range(len(cues)))
    bgm_idx = len(cues) + 1
    if bgm is not None:
        v = max(0.0, min(1.0, args.bgm_volume))
        parts.append(
            f"[{bgm_idx}:a]aresample=48000,aformat=channel_layouts=stereo:sample_rates=48000,"
            f"atrim=duration={dstr},asetpts=PTS-STARTPTS,apad=whole_dur={dstr},volume={v}[bgm]"
        )
        n_mix = len(cues) + 2
        parts.append(
            f"[bed]{tts_labels}[bgm]amix=inputs={n_mix}:duration=first:normalize=0[aout]"
        )
    else:
        n_mix = len(cues) + 1
        parts.append(f"[bed]{tts_labels}amix=inputs={n_mix}:duration=first:normalize=0[aout]")
    fc = ";".join(parts)

    cmd: list[str] = [
        "ffmpeg",
        "-y",
        "-i",
        str(video.resolve()),
    ]
    for p in mp3s:
        cmd.extend(["-i", str(p.resolve())])
    if bgm is not None:
        cmd.extend(["-stream_loop", "-1", "-i", str(bgm.resolve())])
    cmd.extend(
        [
            "-filter_complex",
            fc,
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-map",
            "0:s?",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-c:s",
            "copy",
            "-t",
            dstr,
            str(out),
        ]
    )

    out.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(json.dumps({"ffmpeg": cmd}, ensure_ascii=False, indent=2))
        return

    try:
        run(cmd)
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)
        sys.exit(e.returncode or 1)

    print(json.dumps({"output": str(out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
