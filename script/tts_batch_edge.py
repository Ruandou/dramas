#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可选：微软 Edge 在线 TTS（免费额度供个人测试，勿滥用）。
安装：pip install edge-tts

用法：
  python3 video/automation/tts_batch_edge.py --lines 对白.txt --out-dir video/automation/tts_out

对白.txt：一行一句，生成 001.mp3, 002.mp3 … 再在剪映或 ffmpeg 里对齐时间轴。

语速分层（v2.1 基准 Rule 44c 落地）：
  全局：--rate "+10%"（高潮集）/ "-10%"（抒情段），默认 +0%
  行级覆盖：行首加 [rate:+10%] 标记，例：
    [rate:+10%]你给我站住！
    今天……就到这里吧。        ← 用全局 rate
    [rate:-10%]那年冬至，雪下得很大。
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

RATE_TAG = re.compile(r"^\[rate:([+-]\d{1,2}%)\]\s*")


async def run(lines: list[str], out_dir: Path, voice: str, rate: str) -> None:
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
        line_rate = rate
        m = RATE_TAG.match(text)
        if m:
            line_rate = m.group(1)
            text = text[m.end():].strip()
            if not text:
                continue
        idx += 1
        out = out_dir / f"{idx:03d}.mp3"
        communicate = edge_tts.Communicate(text, voice, rate=line_rate)
        await communicate.save(str(out))
        print(f"{out}  (rate {line_rate})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True, help="UTF-8 文本，一行一句")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument(
        "--voice",
        default="zh-CN-XiaoxiaoNeural",
        help="见 edge-tts --list-voices",
    )
    ap.add_argument(
        "--rate",
        default="+0%",
        help='全局语速偏移，如 "+10%%"（高潮）/"-10%%"（抒情）；行级 [rate:±X%%] 标记优先',
    )
    args = ap.parse_args()
    raw = Path(args.lines).read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines()]
    asyncio.run(run(lines, Path(args.out_dir), args.voice, args.rate))


if __name__ == "__main__":
    main()
