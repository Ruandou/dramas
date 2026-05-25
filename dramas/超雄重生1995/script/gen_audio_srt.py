#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transcribe episode MP4 audio to SRT via faster-whisper (HF mirror friendly)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def fmt_ts(sec: float) -> str:
    if sec < 0:
        sec = 0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def extract_audio(video: Path, wav: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(wav),
        ],
        check=True,
        capture_output=True,
    )


def transcribe(wav: Path, *, model: str, language: str) -> list[tuple[float, float, str]]:
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    from faster_whisper import WhisperModel

    whisper = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _info = whisper.transcribe(str(wav), language=language, vad_filter=True)
    cues: list[tuple[float, float, str]] = []
    for seg in segments:
        text = seg.text.strip()
        if text:
            cues.append((seg.start, seg.end, text))
    return cues


def write_srt(cues: list[tuple[float, float, str]], out: Path) -> None:
    blocks: list[str] = []
    for i, (start, end, text) in enumerate(cues, 1):
        blocks.append(f"{i}\n{fmt_ts(start)} --> {fmt_ts(end)}\n{text}\n")
    out.write_text("\n".join(blocks), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Video/audio → SRT (faster-whisper)")
    parser.add_argument("video", type=Path, help="Input MP4 or WAV")
    parser.add_argument("-o", "--output", type=Path, help="Output .srt path")
    parser.add_argument("--model", default="base", help="Whisper model (default: base)")
    parser.add_argument("--lang", default="zh", help="Language code (default: zh)")
    args = parser.parse_args()

    video = args.video.resolve()
    if not video.is_file():
        print(f"ERROR: not found: {video}", file=sys.stderr)
        return 1

    out = args.output or video.with_name(video.stem + "_audio.srt")
    out = out.resolve()

    if video.suffix.lower() == ".wav":
        wav = video
        cleanup = None
    else:
        td = tempfile.mkdtemp(prefix="whisper_")
        wav = Path(td) / "audio.wav"
        cleanup = td
        print(f"Extracting audio from {video.name}…")
        extract_audio(video, wav)

    print(f"Transcribing ({args.model}, {args.lang})…")
    cues = transcribe(wav, model=args.model, language=args.lang)
    write_srt(cues, out)
    print(f"Wrote {len(cues)} cues → {out}")

    if cleanup:
        import shutil

        shutil.rmtree(cleanup, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
