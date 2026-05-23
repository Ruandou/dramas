#!/usr/bin/env python3
"""Convert episode storyboard markdown → EP##_shots.yaml + EP##_shots.json.

Pipeline integration
--------------------
1. Edit   剧本/EP##/EP##_*.md           (storyboard markdown table, human-readable)
2. Run    python3 script/storyboard_to_seedance.py EP01
3. Review 剧本/EP##/EP##_shots.yaml      (machine-readable shot list)
4. Edit   剧本/EP##/EP##_segments.yaml   (merge shots into segments, add voice prompts)
5. Submit storyboard_submit_segments.py EP01 --submit

Usage
-----
    python3 storyboard_to_seedance.py              # EP01, EP02, EP03
    python3 storyboard_to_seedance.py EP01         # single episode
    python3 storyboard_to_seedance.py EP01 EP02    # multiple episodes
    python3 storyboard_to_seedance.py EP01 --with-segments  # also write segments skeleton
    python3 storyboard_to_seedance.py EP01 --validate       # also run era validation
    python3 storyboard_to_seedance.py EP01 --dry-run        # parse only, no file writes

Era
---
《超雄重生1995》 is set in 1995 China.
All prompts must avoid post-1995/post-2000 modern elements.
See 制片规范.md §5 for the full era constraint list.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]   # darams/超雄重生1995/
EPISODE_DIR = ROOT / "剧本"                  # 剧本/EP##/ subdirectories
KEYFRAMES_DIR = ROOT / "assets" / "keyframes"
LOOKS_DIR = ROOT / "assets" / "looks"
SCENES_DIR = ROOT / "assets" / "scenes"


# ---------------------------------------------------------------------------
# Era prompt constants — 1995 China (no historical flashback handling needed)
# ---------------------------------------------------------------------------

# Default suffix appended to every non-skip shot prompt
PROMPT_SUFFIX_1995 = (
    "1995年中国城市，写实电影风格，竖屏9比16，"
    "无智能手机，无平板，无LED广告屏，无现代车型，无清晰广告文字"
)

# Negative prompt included in API body for all shots
NEGATIVE_PROMPT_1995 = (
    "smartphone, flat screen TV, LED lights, modern car, laptop, tablet, "
    "QR code, delivery box, power bank, glass curtain wall, subway station, "
    "LED billboard, Nike logo, Adidas logo, wireless earbuds, bubble tea cup, "
    "modern minimalist interior, neon RGB lighting"
)

# Episode-level defaults written into shots.yaml header
DEFAULTS = {
    "endpoint": "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
    "model": "doubao-seedance-2-0-fast-260128",
    "ratio": "9:16",
    "resolution": "1080x1920",
    "duration": 10,           # seconds; API hard limit: 4–12 for fast model
    "generate_audio": True,   # default: audio-embedded segments workflow
    "watermark": False,
    "prompt_suffix": PROMPT_SUFFIX_1995,
    "negative_prompt": NEGATIVE_PROMPT_1995,
}


# ---------------------------------------------------------------------------
# Inline YAML helpers (no third-party deps required)
# ---------------------------------------------------------------------------

def _yaml_quote(s: str) -> str:
    """Return YAML-safe scalar: bare if simple, quoted otherwise."""
    if re.match(r"^[\w./:-]+$", s) and " " not in s:
        return s
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dump_yaml(obj: object, indent: int = 0) -> str:
    """Serialize a dict/list/scalar to a minimal YAML string."""
    sp = "  " * indent
    if isinstance(obj, dict):
        lines: list[str] = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{sp}{k}:")
                lines.append(dump_yaml(v, indent + 1))
            elif isinstance(v, list) and not v:
                lines.append(f"{sp}{k}: []")
            elif isinstance(v, bool):
                lines.append(f"{sp}{k}: {'true' if v else 'false'}")
            elif isinstance(v, (int, float)):
                lines.append(f"{sp}{k}: {v}")
            elif v is None:
                lines.append(f"{sp}{k}: null")
            else:
                lines.append(f"{sp}{k}: {_yaml_quote(str(v))}")
        return "\n".join(lines)
    if isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, dict):
                lines.append(f"{sp}-")
                inner = dump_yaml(item, indent + 1)
                for ln in inner.splitlines():
                    lines.append(ln)
            else:
                lines.append(f"{sp}- {_yaml_quote(str(item))}")
        return "\n".join(lines)
    return f"{sp}{_yaml_quote(str(obj))}"


def _parse_scalar(raw: str) -> object:
    """Parse a YAML scalar string into Python native types."""
    raw = raw.strip()
    if raw in ("true", "True"):
        return True
    if raw in ("false", "False"):
        return False
    if raw in ("null", "~", ""):
        return None
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.match(r"^-?\d+$", raw):
        return int(raw)
    return raw


def load_yaml(text: str) -> object:
    """Parse a simple YAML string (supports the shots/manifest subset only)."""
    lines = text.splitlines()
    root: object = {}
    stack: list[tuple[int, object]] = [(-1, root)]

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        if stripped.startswith("- ") or stripped == "-":
            if not isinstance(parent, list):
                raise ValueError(f"expected list at indent {indent}")
            val = stripped[2:].strip() if stripped.startswith("- ") else ""
            if val:
                parent.append(_parse_scalar(val))
            else:
                item: dict = {}
                parent.append(item)
                stack.append((indent, item))
            i += 1
            continue

        if ":" not in stripped:
            i += 1
            continue

        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()

        if rest:
            if isinstance(parent, dict):
                parent[key] = _parse_scalar(rest)
            i += 1
            continue

        # Key with nested block on following lines
        peek = i + 1
        if peek < len(lines):
            nxt = lines[peek]
            nxt_indent = len(nxt) - len(nxt.lstrip(" "))
            if nxt_indent > indent and nxt.strip():
                child: object = [] if nxt.strip().startswith("- ") else {}
                if isinstance(parent, dict):
                    parent[key] = child
                stack.append((indent, child))
        i += 1

    return root


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------

def strip_md(s: str) -> str:
    """Remove surrounding backticks, whitespace, and bold markers."""
    return s.strip().strip("`").strip("*").strip()


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter block (--- ... ---) from markdown text."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    result = load_yaml(m.group(1))
    return result if isinstance(result, dict) else {}


def parse_scene_ids(raw: str) -> list[str]:
    """Extract all SCENE-### IDs from a table cell string."""
    raw = strip_md(raw)
    if not raw or raw == "-":
        return []
    return re.findall(r"SCENE-\d+", raw)


def parse_scene_id(raw: str) -> str | None:
    """Return the first SCENE-### ID found, or None."""
    ids = parse_scene_ids(raw)
    return ids[0] if ids else None


def parse_look_ids(raw: str) -> list[str]:
    """Extract CHAR-###-L## or CHAR-GRP-##-L## IDs from a table cell."""
    if not raw or strip_md(raw) == "-":
        return []
    return re.findall(r"CHAR-(?:GRP-\d+|\d+)-L\d+", raw)


def parse_dialogue(note: str) -> list[dict]:
    """
    Extract structured dialogue from the 对白/备注 column.

    Expects format: **CHAR-001**(tone)：dialogue text
    Returns [{"speaker": "CHAR-001", "line": "..."}, ...]
    """
    out: list[dict] = []
    for m in re.finditer(
        r"\*\*(CHAR-[^*]+)\*\*(?:\([^)]*\))?[：:]([^*]+?)(?=\s*\*\*CHAR-|\s*$)",
        note,
    ):
        speaker = m.group(1).strip()
        line = m.group(2).strip().rstrip("。")
        if line:
            out.append({"speaker": speaker, "line": line})
    return out


# ---------------------------------------------------------------------------
# Storyboard table parser
# ---------------------------------------------------------------------------

def parse_table_rows(md_path: Path) -> list[dict]:
    """
    Parse all storyboard table rows from a markdown file.

    Expected table header (must contain both 'shot_id' and '镜号'):
    | shot_id | 镜号 | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 画面 | 运镜 | 对白/备注 |
    """
    text = md_path.read_text(encoding="utf-8")
    rows: list[dict] = []
    headers: list[str] = []
    ready = False

    for line in text.splitlines():
        if not line.strip().startswith("|"):
            # Reset when leaving a table block
            headers = []
            ready = False
            continue

        cells = [c.strip() for c in line.strip().strip("|").split("|")]

        # Separator line (e.g. | --- | :---: |)
        if all(re.match(r"^:?-+:?$", c) for c in cells):
            ready = bool(headers)
            continue

        # Header row: must have both shot_id and 镜号 columns
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


# ---------------------------------------------------------------------------
# Shot entry builder
# ---------------------------------------------------------------------------

def build_api_text(
    运镜: str,
    画面: str,
    mode: str,
    look_ids: list[str],
    scene_id: str | None,
    景别: str = "",
) -> str:
    """
    Assemble the api.text prompt string from storyboard fields.

    For i2v_ref: prepend 【图N】 labels for reference images.
    Always append the 1995-era prompt suffix.
    """
    parts: list[str] = []
    y = strip_md(运镜)
    if y and y != "-":
        parts.append(y)

    jb = strip_md(景别)
    if jb and jb != "-":
        # Map Chinese shot type to prompt keyword
        jb_map = {
            "特写": "镜头特写",
            "近景": "镜头近景",
            "中景": "镜头中景",
            "全景": "镜头全景",
            "主观": "主观镜头",
            "跟拍": "镜头跟随",
            "慢镜": "慢动作",
        }
        parts.append(jb_map.get(jb, jb))

    parts.append(strip_md(画面))
    body = "，".join(p for p in parts if p)

    # For reference-image modes, prepend [图N] labels
    if mode == "i2v_ref":
        labels: list[str] = []
        for idx, lid in enumerate(look_ids, 1):
            labels.append(f"【图{idx}】{lid}")
        if scene_id:
            labels.append(f"【图{len(look_ids) + 1}】{scene_id}")
        prefix = "".join(labels) + "。"
        body = prefix + body

    return f"{body}。{PROMPT_SUFFIX_1995}"


def shot_to_yaml_entry(row: dict, ep_id: str) -> dict:
    """Convert a single storyboard table row into a shots.yaml entry dict."""
    shot_id = strip_md(row["shot_id"])
    mode = strip_md(row.get("模式", "i2v"))
    duration_raw = strip_md(row.get("时长", "10"))
    duration_sec = None if duration_raw in ("-", "") else int(duration_raw)

    entry: dict = {
        "shot_id": shot_id,
        "shot_no": int(re.sub(r"\D", "", strip_md(row.get("镜号", "0"))) or 0),
        "mode": mode,
    }
    if duration_sec is not None:
        entry["duration_sec"] = duration_sec

    scene_id = parse_scene_id(row.get("场景", ""))
    look_ids = parse_look_ids(row.get("形象", ""))

    # skip: black screen / title card — merged into adjacent segment
    if mode == "skip":
        note = strip_md(row.get("对白/备注", ""))
        if note and note != "-":
            entry["note"] = note
        return entry

    # refs block: which IDs are referenced
    if scene_id or look_ids:
        refs: dict = {}
        if scene_id:
            refs["scene_id"] = scene_id
        if look_ids:
            refs["look_ids"] = look_ids
        entry["refs"] = refs

    # assets block: local file paths
    assets: dict = {}
    if mode in ("i2v", "i2v_ref", "i2v_ff"):
        assets["first_frame"] = (
            f"assets/keyframes/{ep_id}/{shot_id}_first.png"
        )
    if mode == "i2v_ref":
        if look_ids:
            assets["look_urls"] = {
                lid: f"assets/looks/{lid}.png" for lid in look_ids
            }
        if scene_id:
            assets["scene_urls"] = {scene_id: f"assets/scenes/{scene_id}.png"}
    if assets:
        entry["assets"] = assets

    # content_roles: order determines 【图N】 references in api.text
    content_roles: list[dict] = []
    if mode == "i2v_ref":
        for idx, lid in enumerate(look_ids, 1):
            content_roles.append(
                {"file": lid, "role": "reference_image", "label": f"图{idx}"}
            )
        if scene_id:
            content_roles.append(
                {
                    "file": scene_id,
                    "role": "reference_image",
                    "label": f"图{len(look_ids) + 1}",
                }
            )
        content_roles.append({"file": "first_frame", "role": "first_frame"})
    elif mode in ("i2v", "i2v_ff"):
        content_roles.append({"file": "first_frame", "role": "first_frame"})

    api: dict = {
        "text": build_api_text(
            row.get("运镜", ""),
            row.get("画面", ""),
            mode,
            look_ids,
            scene_id,
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


# ---------------------------------------------------------------------------
# Keyframes manifest
# ---------------------------------------------------------------------------

def build_manifest(ep_id: str, shots: list[dict]) -> dict:
    """
    Build a keyframes/EP##/manifest.yaml that lists required first-frame images.

    This manifest is useful for checking 'are all keyframes ready?' before
    submitting API tasks.
    """
    required: list[dict] = []
    looks_needed: set[str] = set()
    scenes_needed: set[str] = set()

    for s in shots:
        if s.get("mode") == "skip":
            continue
        item: dict = {
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


# ---------------------------------------------------------------------------
# Segments skeleton builder
# ---------------------------------------------------------------------------

def build_segments_skeleton(ep_id: str, shots: list[dict]) -> dict:
    """
    Build a minimal EP##_segments_skeleton.yaml as a starting point.

    Each non-skip shot becomes its own segment placeholder.
    In practice, adjacent shots from the same scene should be merged.
    See 制片规范.md §8 for merging rules (4–12 s per segment).

    This skeleton is meant to be hand-edited into EP##_segments.yaml.
    """
    segments: list[dict] = []
    seg_no = 1

    for s in shots:
        if s.get("mode") == "skip":
            continue
        seg_id = f"{ep_id}-SEG{seg_no:02d}"
        seg_no += 1

        # Harvest dialogue speakers for voice_prompt scaffolding
        dlg = s.get("dialogue") or []
        speakers: list[str] = [d["speaker"] for d in dlg]

        seg: dict = {
            "segment_id": seg_id,
            "shot_ids": [s["shot_id"]],
            "duration_sec": s.get("duration_sec", DEFAULTS["duration"]),
            "generate_audio": True,
        }
        if speakers:
            seg["speakers"] = speakers
            # Placeholder voice_prompt — fill in from 角色卡.md
            seg["voice_prompt"] = "TODO: fill from 角色卡.md voice_prompt field"

        api_text = (s.get("api") or {}).get("text", "")
        seg["api"] = {
            "text": api_text,
            # NOTE: Add content_roles from shots.yaml refs before submitting
        }
        segments.append(seg)

    return {
        "episode_id": ep_id,
        "note": (
            "Auto-generated skeleton — hand-edit before submission. "
            "Merge adjacent shots (same scene/speaker) into one segment. "
            "Each segment must be 4–12 s. See 制片规范.md §8."
        ),
        "defaults": {
            "model": DEFAULTS["model"],
            "ratio": DEFAULTS["ratio"],
            "resolution": DEFAULTS["resolution"],
            "generate_audio": True,
            "watermark": False,
        },
        "segments": segments,
    }


# ---------------------------------------------------------------------------
# Era validation stub
# ---------------------------------------------------------------------------

# Post-1995 / modern keywords that must NOT appear in shot prompts
_MODERN_KEYWORDS = re.compile(
    r"smartphone|iphone|android|flat.?screen|LED.?TV|laptop|tablet|ipad|"
    r"QR.?code|quick.?response.?code|delivery.?box|takeout|power.?bank|"
    r"glass.?curtain.?wall|subway|metro|high.?speed.?rail|electric.?scooter|"
    r"LED.?billboard|Nike|Adidas|wireless.?earbuds|AirPods|bubble.?tea.?cup|"
    r"modern.?minimalist|neon.?RGB|ring.?light|selfie|social.?media|"
    r"二维码|智能手机|平板电脑|液晶电视|LED广告|外卖箱|充电宝|无线耳机|奶茶杯",
    re.IGNORECASE,
)


def validate_era_shots(shots: list[dict], ep_id: str) -> list[str]:
    """
    Stub: scan api.text in each non-skip shot for post-1995 keywords.

    Returns a list of error/warning strings. Empty list = pass.
    Extend _MODERN_KEYWORDS as more patterns are discovered.
    """
    issues: list[str] = []
    for s in shots:
        if s.get("mode") == "skip":
            continue
        api_text = (s.get("api") or {}).get("text", "")
        m = _MODERN_KEYWORDS.search(api_text)
        if m:
            issues.append(
                f"  ⚠ {ep_id} {s['shot_id']}: possible post-1995 keyword "
                f"'{m.group(0)}' in api.text"
            )
    return issues


# ---------------------------------------------------------------------------
# Episode export
# ---------------------------------------------------------------------------

def export_episode(
    md_path: Path,
    with_segments: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Parse one episode storyboard markdown and write output YAML/JSON files.

    Output files (in 剧本/EP##/):
      - EP##_shots.yaml        machine-readable shot list
      - EP##_shots.json        same data as JSON (for tooling)
      - EP##_segments_skeleton.yaml  (only if with_segments=True)

    Output files (in assets/keyframes/EP##/):
      - manifest.yaml          list of required first-frame images
    """
    text = md_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    ep_id: str = fm.get("episode_id") or md_path.stem.split("_")[0].upper()
    ep_dir = md_path.parent  # 剧本/EP##/

    rows = parse_table_rows(md_path)
    if not rows:
        print(
            f"  [warn] No storyboard table rows found in {md_path.name}",
            file=sys.stderr,
        )

    shots = [shot_to_yaml_entry(r, ep_id) for r in rows]

    # Build output data
    out_shots: dict = {
        "episode_id": ep_id,
        "source_md": str(md_path.relative_to(ROOT)),
        "defaults": DEFAULTS,
        "shots": shots,
    }
    manifest = build_manifest(ep_id, shots)

    if dry_run:
        print(
            f"[dry-run] {ep_id}: {len(shots)} shots parsed "
            f"({sum(1 for s in shots if s.get('mode') != 'skip')} active)"
        )
        return

    # Write shots YAML
    ep_dir.mkdir(parents=True, exist_ok=True)
    shots_path = ep_dir / f"{ep_id}_shots.yaml"
    shots_path.write_text(dump_yaml(out_shots) + "\n", encoding="utf-8")

    # Write shots JSON
    json_path = ep_dir / f"{ep_id}_shots.json"
    json_path.write_text(
        json.dumps(out_shots, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Write keyframes manifest
    manifest_dir = KEYFRAMES_DIR / ep_id
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest.yaml"
    manifest_path.write_text(dump_yaml(manifest) + "\n", encoding="utf-8")

    active = sum(1 for s in shots if s.get("mode") != "skip")
    print(
        f"[ok] {ep_id}: {shots_path.relative_to(ROOT)} "
        f"({len(shots)} shots, {active} active)"
    )
    print(f"     {json_path.relative_to(ROOT)}")
    print(
        f"     {manifest_path.relative_to(ROOT)} "
        f"({len(manifest['required'])} keyframes needed)"
    )

    # Optional: segments skeleton
    if with_segments:
        skel = build_segments_skeleton(ep_id, shots)
        skel_path = ep_dir / f"{ep_id}_segments_skeleton.yaml"
        skel_path.write_text(dump_yaml(skel) + "\n", encoding="utf-8")
        print(
            f"     {skel_path.relative_to(ROOT)} "
            f"({len(skel['segments'])} segment placeholders)"
        )


# ---------------------------------------------------------------------------
# Era validation entry point
# ---------------------------------------------------------------------------

def run_validate(ep_ids: list[str]) -> int:
    """Run era validation on exported shots YAMLs. Returns 0 if all pass."""
    all_issues: list[str] = []
    checked = 0

    for ep_id in ep_ids:
        ep_dir = EPISODE_DIR / ep_id
        shots_yaml = ep_dir / f"{ep_id}_shots.yaml"
        if not shots_yaml.is_file():
            print(
                f"  [skip] {ep_id}_shots.yaml not found — run export first",
                file=sys.stderr,
            )
            continue
        # Re-parse shots JSON (simpler than re-running full YAML load)
        json_path = ep_dir / f"{ep_id}_shots.json"
        if json_path.is_file():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            shots = data.get("shots", [])
        else:
            print(
                f"  [skip] {ep_id}_shots.json not found", file=sys.stderr
            )
            continue

        issues = validate_era_shots(shots, ep_id)
        all_issues.extend(issues)
        checked += 1

    if all_issues:
        print("Era validation issues:")
        for issue in all_issues:
            print(issue)
        return 1

    if checked > 0:
        print(f"[ok] Era validation passed ({checked} episode(s) checked)")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert 《超雄重生1995》 episode storyboard markdown "
            "→ EP##_shots.yaml + EP##_shots.json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 storyboard_to_seedance.py\n"
            "  python3 storyboard_to_seedance.py EP01\n"
            "  python3 storyboard_to_seedance.py EP01 EP02 --with-segments\n"
            "  python3 storyboard_to_seedance.py EP01 --validate --dry-run\n"
        ),
    )
    parser.add_argument(
        "episodes",
        nargs="*",
        metavar="EP##",
        default=["EP01", "EP02", "EP03"],
        help="Episode IDs to process (default: EP01 EP02 EP03)",
    )
    parser.add_argument(
        "--with-segments",
        action="store_true",
        help="Also write EP##_segments_skeleton.yaml (hand-edit before use)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run era validation after export (checks for post-1995 keywords)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse only — report shot counts without writing any files",
    )

    args = parser.parse_args()
    ep_ids: list[str] = [ep.upper() for ep in args.episodes]

    any_exported = False
    for ep_id in ep_ids:
        ep_dir = EPISODE_DIR / ep_id
        if not ep_dir.is_dir():
            print(
                f"  [warn] Episode directory not found: {ep_dir.relative_to(ROOT)}",
                file=sys.stderr,
            )
            continue

        # Find storyboard markdown (exclude shots/segments YAML and _模板.md)
        matches = [
            p for p in ep_dir.glob(f"{ep_id}_*.md")
            if "_shots" not in p.name
            and "_segments" not in p.name
            and p.name != "_模板.md"
        ]
        if not matches:
            print(
                f"  [warn] No storyboard markdown found for {ep_id} "
                f"in {ep_dir.relative_to(ROOT)}",
                file=sys.stderr,
            )
            continue

        export_episode(
            matches[0],
            with_segments=args.with_segments,
            dry_run=args.dry_run,
        )
        any_exported = True

    if not any_exported:
        print(
            "No episodes exported. "
            "Create 剧本/EP##/EP##_*.md with a storyboard table first.",
            file=sys.stderr,
        )
        return 1

    if args.validate and not args.dry_run:
        return run_validate(ep_ids)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
