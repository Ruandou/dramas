#!/usr/bin/env python3
"""校验分镜 shots 与定妆 batch 的年代一致性（只读）。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODE_DIR = ROOT / "分集剧本"
LOOKS_BATCH = ROOT / "assets" / "looks" / "seedream_batch.yaml"

FLASHBACK_SCENES = frozenset({"SCENE-004"})
MING_FORBIDDEN_IN_FLASHBACK = "无现代物品"
MODERN_WARNINGS = re.compile(
    r"library|smartphone|wristwatch|sports watch|keyboard|neon sign",
    re.I,
)
LOOKS_FORBIDDEN = re.compile(r"deep\s*v|off-shoulder|off shoulder", re.I)


def iter_shots_from_yaml(path: Path) -> list[tuple[str, str | None, str]]:
    """返回 (shot_id, scene_id, api_text) 列表。"""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n  - shot_id:", text)
    out: list[tuple[str, str | None, str]] = []
    for block in blocks[1:]:
        sid_m = re.match(r" (\S+)", block)
        if not sid_m:
            continue
        sid = sid_m.group(1).strip()
        if re.search(r"\n    mode: skip\n", block):
            continue
        scene_m = re.search(r"scene_id: (SCENE-\d+)", block)
        scene_id = scene_m.group(1) if scene_m else None
        text_m = re.search(r'\n      text: "((?:[^"\\]|\\.)*)"', block)
        api_text = text_m.group(1) if text_m else ""
        api_text = api_text.replace("\\n", "\n")
        out.append((sid, scene_id, api_text))
    return out


def check_shots_yaml(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for sid, scene_id, api_text in iter_shots_from_yaml(path):
        scene_ids = {scene_id} if scene_id else set()
        if FLASHBACK_SCENES.intersection(scene_ids) and MING_FORBIDDEN_IN_FLASHBACK in api_text:
            errors.append(
                f"{path.name} {sid}: SCENE-004 与「无现代物品」同条 prompt"
            )
        if "闪回" in api_text and MING_FORBIDDEN_IN_FLASHBACK in api_text and (
            "flashback overlay" not in api_text
        ):
            errors.append(
                f"{path.name} {sid}: 闪回镜应使用 flashback 后缀，不应含「无现代物品」"
            )
        if scene_id not in FLASHBACK_SCENES and MODERN_WARNINGS.search(api_text):
            warnings.append(
                f"{path.name} {sid}: 非 SCENE-004 但 text 含现代场景词（{scene_id}）"
            )
    return errors, warnings


def check_looks_batch(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return errors
    text = path.read_text(encoding="utf-8")
    for m in LOOKS_FORBIDDEN.finditer(text):
        errors.append(f"{path.name}: 含禁词「{m.group(0)}」（本剧古装，见年代美术规范）")
    return errors


def main(argv: list[str]) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    yaml_files = sorted(EPISODE_DIR.glob("EP*_shots.yaml"))
    if not yaml_files:
        print("未找到 EP*_shots.yaml", file=sys.stderr)
        return 1

    for yf in yaml_files:
        e, w = check_shots_yaml(yf)
        errors.extend(e)
        warnings.extend(w)

    errors.extend(check_looks_batch(LOOKS_BATCH))

    if warnings:
        print("警告:")
        for w in warnings:
            print(f"  ⚠ {w}")
    if errors:
        print("错误:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print(f"OK · 已检查 {len(yaml_files)} 个 shots 文件")
    if warnings:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
