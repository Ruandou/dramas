#!/usr/bin/env python3
"""Repair EP01_shots.yaml list structure and re-dump without YAML anchors."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

PATH = Path(__file__).resolve().parents[1] / "剧本" / "EP01" / "EP01_shots.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data) -> bool:
        return True


def parse_shot_block(block: str) -> dict:
    lines = block.splitlines()
    cleaned = []
    for line in lines:
        if line.startswith("  "):
            cleaned.append(line[2:])
        elif line.startswith("- "):
            cleaned.append(line[2:])
        else:
            cleaned.append(line)
    text = "\n".join(cleaned).strip()
    text = re.sub(r" &\w+", "", text)
    text = re.sub(r" \*\w+", "", text)
    return yaml.safe_load(text)


def repair() -> None:
    raw = PATH.read_text(encoding="utf-8")
    m = re.search(r"^shots:\s*$", raw, re.M)
    if not m:
        raise SystemExit("shots: marker not found")
    header = raw[: m.start()]
    body = raw[m.end() :]

    parts = re.split(r"(?=^\s{2}shot_id: EP01-S\d+)", body, flags=re.M)
    shots = []
    for part in parts:
        part = part.strip()
        if not part or not part.startswith("shot_id"):
            continue
        shot = parse_shot_block(part)
        api = shot.get("api") or {}
        roles = api.get("content_roles") or []
        for i, role in enumerate(roles):
            role["label"] = f"图{i + 1}"
        if shot.get("mode") == "i2v_ref" and "api" in shot:
            shot["api"]["return_last_frame"] = True
        if shot.get("mode") == "skip":
            shot["duration_sec"] = 0
        shots.append(shot)

    shots.sort(key=lambda s: int(s["shot_id"].split("-S")[1]))
    if len(shots) != 32:
        raise SystemExit(f"expected 32 shots, got {len(shots)}: {[s['shot_id'] for s in shots]}")

    meta = yaml.safe_load(re.sub(r"^#.*\n", "", header, count=1))
    meta["shots"] = shots
    comment = "# EP01 shots — 29 effective + 3 skip, 13 API segments · 134s\n"
    out = comment + yaml.dump(
        meta,
        allow_unicode=True,
        sort_keys=False,
        Dumper=NoAliasDumper,
        width=120,
    )
    PATH.write_text(out, encoding="utf-8")
    total = sum(s.get("duration_sec") or 0 for s in shots)
    print(f"repaired {len(shots)} shots, duration sum {total}s")


if __name__ == "__main__":
    repair()
