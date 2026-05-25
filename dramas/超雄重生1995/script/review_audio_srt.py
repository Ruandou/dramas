#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Review Whisper SRT against segments.yaml dialogue_lines.
Keeps timestamps; fixes homophones and obvious ASR errors when match is confident.
"""

from __future__ import annotations

import argparse
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

import yaml


def find_project_root(start: Path) -> Path:
    p = start.resolve().parent
    for _ in range(8):
        if (p / "剧本").is_dir() and (p / "script").is_dir():
            return p
        p = p.parent
    raise FileNotFoundError(f"cannot find project root from {start}")


def normalize(text: str) -> str:
    return re.sub(r"[\s，。！？、；：""''—…\-·\.!?\"'（）()【】\[\]《》]", "", text)


def load_dialogue_lines(segments_yaml: Path) -> list[str]:
    data = yaml.safe_load(segments_yaml.read_text(encoding="utf-8"))
    lines: list[str] = []
    for seg in data.get("segments") or []:
        for item in seg.get("dialogue_lines") or []:
            text = (item.get("text") or "").strip()
            if text:
                lines.append(text)
    return lines


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    raw = path.read_text(encoding="utf-8-sig").strip()
    cues: list[tuple[float, float, str]] = []
    for block in re.split(r"\n\s*\n+", raw):
        rows = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        if len(rows) < 2:
            continue
        i = 1 if re.match(r"^\d+\s*$", rows[0]) else 0
        m = re.match(
            r"(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d\d):(\d\d):(\d\d)[,.](\d{3})",
            rows[i],
        )
        if not m:
            continue
        t0 = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000
        t1 = int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000
        text = "\n".join(rows[i + 1 :]).strip()
        if text:
            cues.append((t0, t1, text))
    return cues


def fmt_ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues: list[tuple[float, float, str]], out: Path) -> None:
    blocks = [f"{i}\n{fmt_ts(t0)} --> {fmt_ts(t1)}\n{text}\n" for i, (t0, t1, text) in enumerate(cues, 1)]
    out.write_text("\n".join(blocks), encoding="utf-8")


def score(a: str, b: str) -> float:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    if na in nb or nb in na:
        return max(SequenceMatcher(None, na, nb).ratio(), 0.72)
    return SequenceMatcher(None, na, nb).ratio()


def pick_script_line(
    whisper: str,
    script_lines: list[str],
    cursor: int,
    *,
    window: int = 8,
    min_score: float = 0.48,
) -> tuple[int, str | None, float]:
    wn = normalize(whisper)
    best_idx = cursor
    best_score = 0.0
    best_text: str | None = None
    end = min(len(script_lines), cursor + window)
    for i in range(cursor, end):
        s = script_lines[i]
        sc = score(whisper, s)
        if sc > best_score:
            best_score = sc
            best_idx = i
            best_text = s
    if best_score < min_score or best_text is None:
        return cursor, None, best_score
    return best_idx, best_text, best_score


def shorten_to_whisper(script: str, whisper: str) -> str:
    """If script is longer than spoken chunk, keep clause best matching whisper."""
    if len(normalize(script)) <= len(normalize(whisper)) * 1.35:
        return script
    parts = re.split(r"(?<=[。！？；])", script)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return script
    best = script
    best_sc = score(whisper, script)
    acc = ""
    for p in parts:
        acc = (acc + p).strip()
        sc = score(whisper, acc)
        if sc >= best_sc:
            best_sc = sc
            best = acc
        if sc >= 0.85:
            break
    return best


def apply_homophone_fixes(text: str) -> tuple[str, list[str]]:
    """Conservative in-place fixes for common Whisper homophones in this project."""
    rules: list[tuple[str, str]] = [
        ("行政棵", "刑侦科"),
        ("行政科", "刑侦科"),
        ("老成家", "老同志"),
        ("还历所", "还利索"),
        ("时辈", "十倍"),
        ("擅门", "扇门"),
        ("记忆供电", "记忆宫殿"),
        ("卷踪", "卷宗"),
        ("随时掉取", "随时调取"),
        ("升级网", "升级我"),
        ("每迫", "每破"),
        ("没迫", "没破"),
        ("微迫", "未破"),
        ("本事形式", "本市刑事"),
        ("番疏", "翻书"),
        ("当案事", "档案室"),
        ("印燃厂", "印染厂"),
        ("资源外出", "自愿外出"),
        ("资源出走", "自愿出走"),
        ("案件隔制", "案件搁置"),
        ("访职机械厂", "纺织机械厂"),
        ("见隔", "间隔"),
        ("案节", "按节奏"),
        ("加进困难", "家境困难"),
        ("厂内手人", "厂内熟人"),
        ("通计", "通气"),
        ("小洛", "小陆"),
        ("经历旺盛", "精力挺旺盛"),
        ("家务事儿", "家务事"),
        ("分轻主赐", "分清主次"),
        ("赵副斗云", "赵指导员"),
        ("贵词", "柜子"),
        ("所生秀", "生锈"),
        ("这份封闭", "这份封皮"),
        ("棉房厂", "棉纺厂"),
        ("十宗", "失踪"),
        ("侠区", "辖区"),
        ("当格案", "当个案"),
        ("同名同性", "同名同姓"),
    ]
    out = text
    changes: list[str] = []
    for wrong, right in rules:
        if wrong in out and wrong != right:
            out = out.replace(wrong, right)
            changes.append(f"{wrong}→{right}")
    return out, changes


def review_cues(
    cues: list[tuple[float, float, str]],
    script_lines: list[str],
    *,
    min_score: float = 0.48,
    max_len_ratio: float = 1.35,
) -> tuple[list[tuple[float, float, str]], list[str]]:
    out: list[tuple[float, float, str]] = []
    logs: list[str] = []
    cursor = 0
    for t0, t1, text in cues:
        fixed, homo_logs = apply_homophone_fixes(text)
        if homo_logs:
            logs.append(f"[{fmt_ts(t0)}] homophone: {', '.join(homo_logs)}")
            logs.append(f"  {text!r} → {fixed!r}")

        idx, script_fix, sc = pick_script_line(fixed, script_lines, cursor, min_score=min_score)
        if script_fix and normalize(script_fix) != normalize(fixed):
            candidate = shorten_to_whisper(script_fix, fixed)
            wlen = max(len(normalize(fixed)), 1)
            clen = len(normalize(candidate))
            if sc >= 0.62 and clen <= wlen * max_len_ratio:
                if normalize(candidate) != normalize(fixed):
                    logs.append(f"[{fmt_ts(t0)}] script ({sc:.2f}): {fixed!r} → {candidate!r}")
                    fixed = candidate
                cursor = idx + 1
            elif idx >= cursor:
                cursor = idx

        out.append((t0, t1, fixed))
    return out, logs


def main() -> int:
    parser = argparse.ArgumentParser(description="Review Whisper SRT vs segments.yaml")
    parser.add_argument("srt", type=Path, help="Whisper SRT")
    parser.add_argument("--segments", type=Path, help="EP##_segments.yaml")
    parser.add_argument("-o", "--output", type=Path, help="Output SRT (default: in-place)")
    parser.add_argument("--min-score", type=float, default=0.48)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    srt = args.srt.resolve()
    if not srt.is_file():
        print(f"ERROR: {srt} not found", file=sys.stderr)
        return 1

    segments = args.segments
    if not segments:
        m = re.search(r"(EP\d+)", srt.stem, re.I)
        if not m:
            print("ERROR: pass --segments or use EP## in srt filename", file=sys.stderr)
            return 1
        ep = m.group(1).upper()
        root = find_project_root(srt)
        segments = root / "剧本" / ep / f"{ep}_segments.yaml"
    segments = segments.resolve()
    if not segments.is_file():
        print(f"ERROR: {segments} not found", file=sys.stderr)
        return 1

    script_lines = load_dialogue_lines(segments)
    cues = parse_srt(srt)
    fixed, logs = review_cues(cues, script_lines, min_score=args.min_score)

    print(f"Script lines: {len(script_lines)}, cues: {len(cues)}, fixes: {len(logs)}")
    for line in logs:
        print(line)

    if args.dry_run:
        return 0

    out = (args.output or srt).resolve()
    write_srt(fixed, out)
    print(f"Wrote → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
