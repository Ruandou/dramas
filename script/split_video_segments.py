#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将成片按固定时长切段（ffmpeg segment，视频轨流复制；默认不复制字幕轨，避免切段后封装异常）。

用法（仓库根）：
  python3 video/automation/split_video_segments.py \\
    --input video/output/第01集_软字幕.mp4 \\
    --out-dir video/output/ep01_5s_split \\
    --segment-time 5

可选：--install-ep01 将 slice_000 … slice_013 复制为 config_ep01.json 中的 14 个镜号文件名到 video/generated/（会覆盖同名文件）。

说明：无音轨时只输出视频；-c copy 切段长度会在关键帧处对齐，可能略长于 --segment-time（常见约 5.04s 对应 5s 设置）。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


EP01_FILENAMES = [
    "第01镜_场1-1A_jimeng.mp4",
    "第02镜_场1-1B_jimeng.mp4",
    "第03镜_场1-1C_jimeng.mp4",
    "第04镜_场1-1D_jimeng.mp4",
    "第05镜_场1-1E_jimeng.mp4",
    "第06镜_场1-2A_jimeng.mp4",
    "第07镜_场1-2B_jimeng.mp4",
    "第08镜_场1-2C_jimeng.mp4",
    "第09镜_场1-2D_jimeng.mp4",
    "第10镜_场1-2E_jimeng.mp4",
    "第11镜_场1-3A_jimeng.mp4",
    "第12镜_场1-3B_jimeng.mp4",
    "第13镜_场1-3C_jimeng.mp4",
    "第14镜_场1-3D_jimeng.mp4",
]


def main() -> None:
    ap = argparse.ArgumentParser(description="按固定秒数切段 MP4（仅视频轨）")
    ap.add_argument("--input", required=True, help="输入成片，相对仓库根或绝对路径")
    ap.add_argument(
        "--out-dir",
        required=True,
        help="输出目录，如 video/output/ep01_5s_split",
    )
    ap.add_argument(
        "--segment-time",
        type=float,
        default=5.0,
        help="目标段长（秒），默认 5；实际长度随关键帧略有浮动",
    )
    ap.add_argument(
        "--prefix",
        default="slice",
        help="输出文件名前缀，生成 prefix_000.mp4 …",
    )
    ap.add_argument(
        "--install-ep01",
        action="store_true",
        help="将生成的 slice_000… 按顺序复制到 video/generated/ 并命名为 14 镜 jimeng 文件名（覆盖同名）",
    )
    args = ap.parse_args()
    root = repo_root()
    inp = Path(args.input)
    if not inp.is_file():
        inp = root / args.input
    if not inp.is_file():
        sys.exit(f"找不到输入: {args.input}")

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(out_dir / f"{args.prefix}_%03d.mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(inp.resolve()),
        "-map",
        "0:v",
        "-c",
        "copy",
        "-f",
        "segment",
        "-segment_time",
        str(args.segment_time),
        "-reset_timestamps",
        "1",
        pattern,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        sys.exit(r.returncode or 1)

    slices = sorted(out_dir.glob(f"{args.prefix}_*.mp4"))
    print(f"已写入 {len(slices)} 段 -> {out_dir}")

    if args.install_ep01:
        if len(slices) != len(EP01_FILENAMES):
            sys.exit(
                f"--install-ep01 需要恰好 {len(EP01_FILENAMES)} 段，当前 {len(slices)} 段，请改 --segment-time 或检查片长。"
            )
        gen = root / "video" / "generated"
        gen.mkdir(parents=True, exist_ok=True)
        for src, name in zip(slices, EP01_FILENAMES):
            dest = gen / name
            shutil.copy2(src, dest)
            print(f"复制 -> video/generated/{name}")


if __name__ == "__main__":
    main()
