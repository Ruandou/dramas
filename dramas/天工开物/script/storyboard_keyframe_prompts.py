#!/usr/bin/env python3
"""
从 shots + 角色卡/场景卡片生成 Seedream 用 Prompt 清单。

产出：
  assets/looks/seedream_batch.yaml
  assets/scenes/seedream_batch.yaml
  assets/keyframes/EP##/seedream_prompts.yaml
"""

from __future__ import annotations
from storyboard_yaml import dump_yaml, load_yaml

import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


ROOT = Path(__file__).resolve().parents[1]
EPISODE_DIR = ROOT / "剧本"
ROLE_CARD = ROOT / "角色卡.md"
SCENE_CARD = ROOT / "资产" / "场景卡片.md"
KEYFRAMES_DIR = ROOT / "assets" / "keyframes"
LOOKS_DIR = ROOT / "assets" / "looks"
SCENES_DIR = ROOT / "assets" / "scenes"

SUFFIX_MARK = "明代苏州，天启年间"
SEEDREAM_SUFFIX = (
    "9:16 vertical portrait, cinematic still frame, photorealistic, "
    "Chinese historical drama Ming dynasty, no readable text, no watermark"
)


def load_episode_shots(ep_id: str) -> dict:
    json_path = EPISODE_DIR / f"{ep_id}_shots.json"
    yaml_path = EPISODE_DIR / f"{ep_id}_shots.yaml"
    if json_path.is_file():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return load_yaml(yaml_path.read_text(encoding="utf-8"))


def parse_codeblock_prompts(md_path: Path, id_pattern: str) -> dict[str, str]:
    """只匹配「形象标题行后紧跟 ``` 代码块」的 Prompt，避免表格里的 ID 误匹配。"""
    text = md_path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for m in re.finditer(
        rf"`({id_pattern})`[^\n]*\n\n```\n([\s\S]*?)\n```",
        text,
    ):
        out[m.group(1)] = m.group(2).strip()
    # **L01** — `prompt` 单行（小翠等）
    for m in re.finditer(
        rf"\*\*L\d+\*\* — `([\s\S]*?)`",
        text,
    ):
        body = m.group(1).strip()
        if "CHAR-004-L01" not in out and "Female Chinese young maid" in body:
            out["CHAR-004-L01"] = body
    return out


def strip_seedance_suffix(text: str) -> str:
    if SUFFIX_MARK in text:
        return text.split(SUFFIX_MARK)[0].rstrip("。，, ")
    return text.rstrip("。，, ")


def _one_line(s: str) -> str:
    return " ".join(s.split())


def build_keyframe_prompt(
    shot: dict,
    look_prompts: dict[str, str],
    scene_prompts: dict[str, str],
) -> str:
    api_text = strip_seedance_suffix((shot.get("api") or {}).get("text", ""))
    # 去掉 【图N】ID 前缀，保留动作描述
    action = re.sub(r"【图\d+】[A-Z0-9-]+", "", api_text).strip("。 ")
    parts = ["First frame storyboard still for vertical short drama shot."]
    refs = shot.get("refs") or {}
    scene_id = refs.get("scene_id")
    if scene_id and scene_id in scene_prompts:
        parts.append(_one_line(scene_prompts[scene_id]))
    for lid in refs.get("look_ids") or []:
        if lid in look_prompts:
            parts.append(f"Character ({lid}): {_one_line(look_prompts[lid])}")
    if action:
        parts.append(f"Action and composition: {action}")
    parts.append(SEEDREAM_SUFFIX)
    return " ".join(parts)


def export_episode(ep_id: str, look_prompts: dict, scene_prompts: dict) -> set[str]:
    episode = load_episode_shots(ep_id)
    items = []
    looks_needed: set[str] = set()
    scenes_needed: set[str] = set()

    for shot in episode.get("shots") or []:
        if shot.get("mode") == "skip":
            continue
        sid = shot["shot_id"]
        assets = shot.get("assets") or {}
        rel = assets.get(
            "first_frame", f"assets/keyframes/{ep_id}/{sid}_first.png")
        refs = shot.get("refs") or {}
        for lid in refs.get("look_ids") or []:
            looks_needed.add(lid)
        if refs.get("scene_id"):
            scenes_needed.add(refs["scene_id"])
        items.append(
            {
                "shot_id": sid,
                "mode": shot.get("mode"),
                "output": rel,
                "depends_on": {
                    "looks": refs.get("look_ids") or [],
                    "scene": refs.get("scene_id"),
                },
                "prompt_en": _one_line(
                    build_keyframe_prompt(shot, look_prompts, scene_prompts)
                ),
                "prompt_zh": strip_seedance_suffix((shot.get("api") or {}).get("text", "")),
            }
        )

    out_dir = KEYFRAMES_DIR / ep_id
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = {
        "episode_id": ep_id,
        "tool": "seedream-4.0",
        "ratio": "9:16",
        "resolution": "720p",
        "notes": "先完成 looks/ 与 scenes/ 定妆与空景，再按序出首帧；L02+ 图生图需 based_on L01",
        "items": items,
    }
    path = out_dir / "seedream_prompts.yaml"
    path.write_text(dump_yaml(doc) + "\n", encoding="utf-8")
    print(f"Wrote {path} ({len(items)} keyframes)")
    return looks_needed, scenes_needed


def write_batch(path: Path, kind: str, ids: set[str], prompts: dict[str, str]) -> None:
    items = []
    for iid in sorted(ids):
        items.append(
            {
                "id": iid,
                "output": f"assets/{kind}/{iid}.png",
                "prompt_en": _one_line(prompts.get(iid, "")),
                "ratio": "9:16",
            }
        )
    doc = {"kind": kind, "tool": "seedream-4.0", "items": items}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(doc) + "\n", encoding="utf-8")
    print(f"Wrote {path} ({len(items)} {kind})")


def main(argv: list[str]) -> None:
    eps = argv[1:] if len(argv) > 1 else ["EP01", "EP02", "EP03"]
    look_prompts = parse_codeblock_prompts(
        ROLE_CARD, r"CHAR-(?:GRP-\d+|\d+)-L\d+")
    scene_prompts = parse_codeblock_prompts(SCENE_CARD, r"SCENE-\d+")

    all_looks: set[str] = set()
    all_scenes: set[str] = set()
    for ep in eps:
        looks, scenes = export_episode(ep.upper(), look_prompts, scene_prompts)
        all_looks |= looks
        all_scenes |= scenes

    write_batch(LOOKS_DIR / "seedream_batch.yaml",
                "looks", all_looks, look_prompts)
    write_batch(SCENES_DIR / "seedream_batch.yaml",
                "scenes", all_scenes, scene_prompts)


if __name__ == "__main__":
    main(sys.argv)
