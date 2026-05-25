#!/usr/bin/env python3
"""从剧本 Markdown 导出 EP##_shots.yaml 与 assets/keyframes/EP##/manifest.yaml"""

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
KEYFRAMES_DIR = ROOT / "assets" / "keyframes"
LOOKS_DIR = ROOT / "assets" / "looks"
SCENES_DIR = ROOT / "assets" / "scenes"

PROMPT_SUFFIX_MING = (
    "明代苏州，天启年间，古风写实，电影感竖屏9比16，无现代物品，无清晰汉字"
)
PROMPT_SUFFIX_FLASHBACK = (
    "flashback overlay, soft blur, 0.5 second cut, cinematic, vertical 9:16, "
    "no readable text"
)
FLASHBACK_SCENE_IDS = frozenset({"SCENE-004"})

# 兼容旧引用
PROMPT_SUFFIX = PROMPT_SUFFIX_MING

DEFAULTS = {
    "endpoint": "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
    "model": "doubao-seedance-2-0-fast-260128",
    "ratio": "9:16",
    "resolution": "720p",
    "duration": 5,
    "generate_audio": False,
    "watermark": False,
    "prompt_suffix": PROMPT_SUFFIX_MING,
    "prompt_suffix_flashback": PROMPT_SUFFIX_FLASHBACK,
}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return load_yaml(m.group(1)) or {}


def strip_md(s: str) -> str:
    return s.strip().strip("`").strip()


def parse_scene_ids(raw: str) -> list[str]:
    raw = strip_md(raw)
    if not raw or raw == "-":
        return []
    return re.findall(r"SCENE-\d+", raw)


def parse_scene_id(raw: str) -> str | None:
    ids = parse_scene_ids(raw)
    return ids[0] if ids else None


def is_flashback_shot(scene_raw: str, 运镜: str, 画面: str, 景别: str = "") -> bool:
    """SCENE-004 或分镜标明闪回 → 用闪回后缀（不含「无现代物品」）。"""
    if FLASHBACK_SCENE_IDS.intersection(parse_scene_ids(scene_raw)):
        return True
    blob = "".join(strip_md(x)
                   for x in (运镜, 画面, 景别) if x and strip_md(x) != "-")
    return "闪回" in blob


def parse_look_ids(raw: str) -> list[str]:
    if not raw or strip_md(raw) == "-":
        return []
    return re.findall(r"CHAR-(?:GRP-\d+|\d+)-L\d+", raw)


def parse_dialogue(note: str) -> list[dict]:
    out = []
    # 支持 **CHAR-001**(哭腔)： 与 **CHAR-009**(VO)：
    for m in re.finditer(
        r"\*\*(CHAR-[^*]+)\*\*(?:\([^)]*\))?[：:]([^*]+?)(?=\s*\*\*CHAR-|\s*$)",
        note,
    ):
        speaker = m.group(1).strip()
        line = m.group(2).strip().rstrip("。")
        if line:
            out.append({"speaker": speaker, "line": line})
    return out


def parse_table_rows(md_path: Path) -> list[dict]:
    text = md_path.read_text(encoding="utf-8")
    rows: list[dict] = []
    headers: list[str] = []
    ready = False

    for line in text.splitlines():
        if not line.strip().startswith("|"):
            headers = []
            ready = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.match(r"^:?-+:?$", c) for c in cells):
            ready = bool(headers)
            continue
        if "shot_id" in cells and "镜号" in cells:
            headers = cells
            ready = False
            continue
        if not ready or not headers or len(cells) < len(headers):
            continue
        row = dict(zip(headers, cells))
        sid = strip_md(row.get("shot_id", ""))
        if sid.startswith("EP"):
            rows.append(row)
    return rows


def pick_prompt_suffix(scene_raw: str, 运镜: str, 画面: str, 景别: str = "") -> str:
    if is_flashback_shot(scene_raw, 运镜, 画面, 景别):
        return PROMPT_SUFFIX_FLASHBACK
    return PROMPT_SUFFIX_MING


def build_api_text(
    运镜: str,
    画面: str,
    mode: str,
    look_ids: list[str],
    scene_id: str | None,
    scene_raw: str = "",
    景别: str = "",
) -> str:
    parts = []
    y = strip_md(运镜)
    if y and y != "-":
        parts.append(y)
    parts.append(strip_md(画面))
    body = "，".join(p for p in parts if p)
    if mode == "i2v_ref":
        labels = []
        for i, lid in enumerate(look_ids, 1):
            labels.append(f"【图{i}】{lid}")
        if scene_id:
            labels.append(f"【图{len(look_ids) + 1}】{scene_id}")
        prefix = "".join(labels) + "。"
        body = prefix + body
    suffix = pick_prompt_suffix(scene_raw, 运镜, 画面, 景别)
    return f"{body}。{suffix}"


def shot_to_yaml_entry(row: dict, ep_id: str) -> dict:
    shot_id = strip_md(row["shot_id"])
    mode = strip_md(row.get("模式", "i2v"))
    duration_raw = strip_md(row.get("时长", "5"))
    duration_sec = None if duration_raw == "-" else int(duration_raw)

    entry: dict = {
        "shot_id": shot_id,
        "shot_no": int(re.sub(r"\D", "", row["镜号"]) or 0),
        "mode": mode,
    }
    if duration_sec is not None:
        entry["duration_sec"] = duration_sec

    scene_id = parse_scene_id(row.get("场景", ""))
    look_ids = parse_look_ids(row.get("形象", ""))

    if mode == "skip":
        note = row.get("对白/备注", "")
        if note:
            entry["note"] = note
        return entry

    if scene_id or look_ids:
        refs = {}
        if scene_id:
            refs["scene_id"] = scene_id
        if look_ids:
            refs["look_ids"] = look_ids
        entry["refs"] = refs

    assets: dict = {}
    if mode in ("i2v", "i2v_ref", "i2v_ff"):
        assets["first_frame"] = f"assets/keyframes/{ep_id}/{shot_id}_first.png"
    if mode == "i2v_ref" and look_ids:
        assets["look_urls"] = {
            lid: f"assets/looks/{lid}.png" for lid in look_ids
        }
    if mode == "i2v_ref" and scene_id:
        assets["scene_urls"] = {scene_id: f"assets/scenes/{scene_id}.png"}
    if assets:
        entry["assets"] = assets

    content_roles = []
    if mode == "i2v_ref":
        idx = 1
        for lid in look_ids:
            content_roles.append(
                {"file": lid, "role": "reference_image", "label": f"图{idx}"})
            idx += 1
        if scene_id:
            content_roles.append(
                {"file": scene_id, "role": "reference_image", "label": f"图{idx}"})
            idx += 1
        content_roles.append({"file": "first_frame", "role": "first_frame"})
    elif mode in ("i2v", "i2v_ff"):
        content_roles.append({"file": "first_frame", "role": "first_frame"})

    api = {
        "text": build_api_text(
            row.get("运镜", ""),
            row.get("画面", ""),
            mode,
            look_ids,
            scene_id,
            scene_raw=row.get("场景", ""),
            景别=row.get("景别", ""),
        ),
    }
    if content_roles:
        api["content_roles"] = content_roles
    if mode == "i2v_ref":
        api["return_last_frame"] = True

    entry["api"] = api
    dlg = parse_dialogue(row.get("对白/备注", ""))
    if dlg:
        entry["dialogue"] = dlg

    return entry


def build_manifest(ep_id: str, shots: list[dict]) -> dict:
    required = []
    looks_needed: set[str] = set()
    scenes_needed: set[str] = set()

    for s in shots:
        if s.get("mode") == "skip":
            continue
        item = {
            "shot_id": s["shot_id"],
            "first_frame": f"{s['shot_id']}_first.png",
            "mode": s["mode"],
        }
        refs = s.get("refs") or {}
        if refs.get("look_ids"):
            item["looks"] = refs["look_ids"]
            looks_needed.update(refs["look_ids"])
        if refs.get("scene_id"):
            item["scene"] = refs["scene_id"]
            scenes_needed.add(refs["scene_id"])
        required.append(item)

    return {
        "episode_id": ep_id,
        "looks_dir": "assets/looks",
        "scenes_dir": "assets/scenes",
        "keyframes_dir": f"assets/keyframes/{ep_id}",
        "unique_looks": sorted(looks_needed),
        "unique_scenes": sorted(scenes_needed),
        "required": required,
    }


def export_episode(md_path: Path) -> None:
    ep_id = parse_frontmatter(md_path.read_text(
        encoding="utf-8")).get("episode_id")
    if not ep_id:
        ep_id = md_path.stem.split("_")[0].upper()

    rows = parse_table_rows(md_path)
    shots = [shot_to_yaml_entry(r, ep_id) for r in rows]

    out_shots = {
        "episode_id": ep_id,
        "source_md": str(md_path.relative_to(ROOT)),
        "defaults": DEFAULTS,
        "shots": shots,
    }

    shots_path = EPISODE_DIR / f"{ep_id}_shots.yaml"
    shots_path.write_text(dump_yaml(out_shots) + "\n", encoding="utf-8")
    json_path = EPISODE_DIR / f"{ep_id}_shots.json"
    json_path.write_text(
        json.dumps(out_shots, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = build_manifest(ep_id, shots)
    manifest_dir = KEYFRAMES_DIR / ep_id
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest.yaml"
    manifest_path.write_text(dump_yaml(manifest) + "\n", encoding="utf-8")

    print(f"Wrote {shots_path} + {json_path} ({len(shots)} shots)")
    print(f"Wrote {manifest_path} ({len(manifest['required'])} keyframes)")


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        eps = ["EP01", "EP02", "EP03"]
    else:
        eps = argv[1:]
    for ep in eps:
        matches = list(EPISODE_DIR.glob(f"{ep}_*.md"))
        matches = [
            m for m in matches if "_shots" not in m.name and m.name != "_模板.md"]
        if not matches:
            print(f"No markdown for {ep}", file=sys.stderr)
            continue
        export_episode(matches[0])


if __name__ == "__main__":
    main(sys.argv)
