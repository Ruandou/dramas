#!/usr/bin/env python3
"""
读取 EP##_shots.yaml → 校验本地素材 → 展开方舟 Seedance API 请求体。

默认 --dry-run（不写 API）；--submit 需 ARK_API_KEY（本地图自动 base64，无需图床）。

用法（在 darams/天工开物 下）：
  python3 script/storyboard_submit_seedance.py EP01
  python3 script/storyboard_submit_seedance.py EP01 --shot EP01-S02
  python3 script/storyboard_submit_seedance.py EP01 --check-only
  export ARK_API_KEY=...
  python3 script/storyboard_submit_seedance.py EP01 --submit
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from storyboard_yaml import load_yaml

ROOT = Path(__file__).resolve().parents[1]
_REPO_SCRIPTS = Path(__file__).resolve().parents[3] / "mcps" / "volc-ark" / "scripts"
if str(_REPO_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_REPO_SCRIPTS))
from ark_media import resolve_image_url  # noqa: E402

EPISODE_DIR = ROOT / "分集剧本"
GENERATED_DIR = ROOT / "assets" / "generated"
REQUESTS_DIR = ROOT / "configs" / "seedance_requests"


def load_episode_shots(ep_id: str) -> dict:
    json_path = EPISODE_DIR / f"{ep_id}_shots.json"
    yaml_path = EPISODE_DIR / f"{ep_id}_shots.yaml"
    if json_path.is_file():
        return json.loads(json_path.read_text(encoding="utf-8"))
    if yaml_path.is_file():
        return load_yaml(yaml_path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"缺少 {json_path} 或 {yaml_path}，请先运行 storyboard_to_seedance.py")


def resolve_asset_path(rel: str) -> Path:
    return (ROOT / rel).resolve()


def collect_asset_paths(shot: dict) -> list[str]:
    assets = shot.get("assets") or {}
    paths: list[str] = []
    for key in ("first_frame", "last_frame"):
        if assets.get(key):
            paths.append(assets[key])
    for mapping in (assets.get("look_urls") or {}).values():
        paths.append(mapping)
    for mapping in (assets.get("scene_urls") or {}).values():
        paths.append(mapping)
    return paths


def validate_shot_assets(shot: dict) -> list[str]:
    missing = []
    for rel in collect_asset_paths(shot):
        p = resolve_asset_path(rel)
        if not p.is_file():
            missing.append(rel)
    return missing


def role_file_to_path(shot: dict, file_key: str) -> str | None:
    assets = shot.get("assets") or {}
    if file_key == "first_frame":
        return assets.get("first_frame")
    if file_key == "last_frame":
        return assets.get("last_frame")
    looks = assets.get("look_urls") or {}
    if file_key in looks:
        return looks[file_key]
    scenes = assets.get("scene_urls") or {}
    if file_key in scenes:
        return scenes[file_key]
    return None


def build_content_array(shot: dict) -> list[dict]:
    api = shot.get("api") or {}
    content: list[dict] = [{"type": "text", "text": api.get("text", "")}]
    for role_spec in api.get("content_roles") or []:
        file_key = role_spec["file"]
        rel = role_file_to_path(shot, file_key)
        if not rel:
            raise ValueError(f"{shot['shot_id']}: 找不到素材 {file_key}")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": resolve_image_url(rel, ROOT)},
                "role": role_spec["role"],
            }
        )
    return content


def build_request_body(episode: dict, shot: dict) -> dict:
    defaults = episode.get("defaults") or {}
    body: dict[str, Any] = {
        "model": defaults.get("model", "doubao-seedance-2-0-fast-260128"),
        "content": build_content_array(shot),
        "ratio": defaults.get("ratio", "9:16"),
        "resolution": defaults.get("resolution", "720p"),
        "duration": shot.get("duration_sec", defaults.get("duration", 5)),
        "generate_audio": defaults.get("generate_audio", False),
        "watermark": defaults.get("watermark", False),
    }
    api = shot.get("api") or {}
    if api.get("return_last_frame"):
        body["return_last_frame"] = True
    if api.get("seed") is not None:
        body["seed"] = api["seed"]
    return body


def post_task(endpoint: str, api_key: str, body: dict) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {detail or e.reason}") from e


def append_task_log(ep_id: str, entry: dict) -> None:
    log_dir = GENERATED_DIR / ep_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "task_log.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seedance 分镜提交（默认 dry-run）")
    parser.add_argument("episode", help="如 EP01")
    parser.add_argument("--shot", help="仅处理指定 shot_id")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="只检查本地素材是否存在",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="真正 POST（需 ARK_API_KEY）",
    )
    parser.add_argument(
        "--cdn-base",
        default=os.environ.get("SEEDANCE_CDN_BASE", "").strip(),
        help="（已废弃，忽略）现用本地 data URI",
    )
    args = parser.parse_args(argv)

    ep_id = args.episode.upper()
    episode = load_episode_shots(ep_id)
    defaults = episode.get("defaults") or {}
    endpoint = defaults.get(
        "endpoint",
        "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
    )

    shots = episode.get("shots") or []
    if args.shot:
        shots = [s for s in shots if s.get("shot_id") == args.shot]
        if not shots:
            print(f"未找到镜头 {args.shot}", file=sys.stderr)
            return 1

    req_dir = REQUESTS_DIR / ep_id
    req_dir.mkdir(parents=True, exist_ok=True)

    missing_all: list[str] = []
    skipped = 0
    ready = 0

    for shot in shots:
        sid = shot.get("shot_id", "?")
        mode = shot.get("mode", "")
        if mode == "skip":
            skipped += 1
            continue

        miss = validate_shot_assets(shot)
        if miss:
            missing_all.extend(f"{sid}: {m}" for m in miss)
            if args.check_only:
                print(f"✗ {sid} 缺 {len(miss)} 个文件")
            continue

        ready += 1
        if args.check_only:
            print(f"✓ {sid} 素材齐全")
            continue

        body = build_request_body(episode, shot)
        out_path = req_dir / f"{sid}.json"
        out_path.write_text(
            json.dumps(body, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"→ {out_path.relative_to(ROOT)}")

        if args.submit:
            key = (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY") or "").strip()
            if not key:
                print("提交需要 ARK_API_KEY", file=sys.stderr)
                return 1
            result = post_task(endpoint, key, body)
            task_id = result.get("id") or result.get("task_id") or result.get("data", {}).get("id")
            print(f"  submitted {sid} task_id={task_id}")
            append_task_log(
                ep_id,
                {
                    "ts": time.time(),
                    "shot_id": sid,
                    "task_id": task_id,
                    "response": result,
                },
            )
            time.sleep(0.5)

    print(
        f"\n{ep_id}: skip={skipped} ready={ready} missing_entries={len(missing_all)}"
    )
    if missing_all and not args.check_only:
        print("\n缺失素材（需 Seedream 首帧/定妆/场景图）：")
        for line in missing_all[:30]:
            print(f"  - {line}")
        if len(missing_all) > 30:
            print(f"  … 另有 {len(missing_all) - 30} 条")

    if missing_all and args.check_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
