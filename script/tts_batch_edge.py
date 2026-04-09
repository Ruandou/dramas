#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可选：微软 Edge 在线 TTS（免费额度供个人测试，勿滥用）。
安装：pip install edge-tts

用法：
  python3 video/automation/tts_batch_edge.py --lines 对白.txt --out-dir video/automation/tts_out

对白.txt：一行一句，生成 001.mp3, 002.mp3 … 再在剪映或 ffmpeg 里对齐时间轴。
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


async def run(lines: list[str], out_dir: Path, voice: str) -> None:
    try:
        import edge_tts
    except ImportError:
        print("请先: pip install edge-tts", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    idx = 0
    for text in lines:
        text = text.strip()
        if not text:
            continue
        idx += 1
        out = out_dir / f"{idx:03d}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out))
        print(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True, help="UTF-8 文本，一行一句")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument(
        "--voice",
        default="zh-CN-XiaoxiaoNeural",
        help="见 edge-tts --list-voices",
    )
    args = ap.parse_args()
    raw = Path(args.lines).read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines()]
    asyncio.run(run(lines, Path(args.out_dir), args.voice))


if __name__ == "__main__":
    main()
