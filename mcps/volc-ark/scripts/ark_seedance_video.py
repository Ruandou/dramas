#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山方舟 · Doubao Seedance 2.0 视频生成（异步任务 API）

文档：
  - 教程：https://www.volcengine.com/docs/82379/2291680?lang=zh
  - API：https://www.volcengine.com/docs/82379/1393047?lang=zh

鉴权：Bearer ARK_API_KEY
接口：
  POST   /api/v3/contents/generations/tasks
  GET    /api/v3/contents/generations/tasks/{id}
  GET    /api/v3/contents/generations/tasks

CLI：
  python3 ark_seedance_video.py docs
  python3 ark_seedance_video.py create --body-json task.json
  python3 ark_seedance_video.py create --text "..." --image-url https://...
  python3 ark_seedance_video.py get --task-id cgt-xxx
  python3 ark_seedance_video.py list --status succeeded
  python3 ark_seedance_video.py wait --task-id cgt-xxx
  python3 ark_seedance_video.py download --task-id cgt-xxx -o out.mp4
  python3 ark_seedance_video.py shots EP01 --project-root .../天工开物 --cdn-base https://...
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from ark_archive import list_tasks as list_local_tasks
from ark_seedance_record import (
    archive_params_from_body,
    record_status,
    record_submit,
    summarize_content,
)
from ark_common import (
    TASKS_PATH,
    api_key,
    base_url,
    download_url,
    extract_task_list,
    extract_video_url,
    http_request,
    safe_mp4_name,
    task_id_from_response,
    task_status,
)
from ark_media import resolve_image_url, resolve_media_url

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

DEFAULT_MODEL = "doubao-seedance-2-0-fast-260128"
DEFAULT_ENDPOINT_SUFFIX = TASKS_PATH


def default_model() -> str:
    import os

    return (os.environ.get("ARK_SEEDANCE_MODEL") or DEFAULT_MODEL).strip()


def build_content_from_simple(
    text: str,
    image_urls: list[tuple[str, str]] | None = None,
    project_root: Path | None = None,
) -> list[dict[str, Any]]:
    """image_urls: [(path_or_url, role), ...] 本地路径自动转 data URI，无需图床"""
    content: list[dict[str, Any]] = [{"type": "text", "text": text}]
    for ref, role in image_urls or []:
        url = resolve_image_url(ref, project_root)
        item: dict[str, Any] = {
            "type": "image_url",
            "image_url": {"url": url},
        }
        if role:
            item["role"] = role
        content.append(item)
    return content


def sanitize_body_for_log(body: dict[str, Any]) -> dict[str, Any]:
    import copy

    b = copy.deepcopy(body)
    if isinstance(b.get("content"), list):
        for item in b["content"]:
            if item.get("type") == "image_url":
                u = (item.get("image_url") or {}).get("url") or ""
                if u.startswith("data:") and len(u) > 120:
                    item["image_url"]["url"] = u[:80] + f"...<{len(u)} chars>"
    return b


def create_task(
    body: dict[str, Any],
    dry_run: bool = False,
    archive_meta: dict | None = None,
) -> dict[str, Any]:
    if dry_run:
        return {
            "status": "dry_run",
            "endpoint": base_url() + TASKS_PATH,
            "body": sanitize_body_for_log(body),
        }
    resp = http_request("POST", TASKS_PATH, body=body, timeout=180)
    tid = task_id_from_response(resp)
    if tid and archive_meta:
        proot = archive_meta.get("project_root")
        if proot:
            record_submit(
                tid,
                body,
                project_root=proot,
                episode=str(archive_meta.get("episode") or ""),
                project_name=str(archive_meta.get("project") or "天工开物"),
                segment_id=archive_meta.get("segment_id"),
                shot_id=archive_meta.get("shot_id"),
            )
    return {
        "status": "submitted",
        "task_id": tid,
        "response": resp,
        "archive": get_archive_base_hint(),
    }


def get_archive_base_hint() -> str:
    from ark_archive import get_archive_base

    return get_archive_base()


def get_task(task_id: str) -> dict[str, Any]:
    path = f"{TASKS_PATH}/{task_id.strip()}"
    resp = http_request("GET", path, timeout=60)
    st = task_status(resp)
    vu = extract_video_url(resp)
    record_status(task_id, st or "unknown", video_url=vu)
    return {
        "task_id": task_id,
        "status": st,
        "video_url": vu,
        "task": resp,
    }


def list_tasks(
    status: str | None = None,
    model: str | None = None,
    page_size: int = 50,
    max_pages: int = 5,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        q: dict[str, str] = {
            "page_num": str(page),
            "page_size": str(min(page_size, 500)),
        }
        if status:
            q["filter.status"] = status
        if model:
            q["filter.model"] = model
        data = http_request("GET", TASKS_PATH, query=q, timeout=60)
        batch = extract_task_list(data)
        if not batch and isinstance(data, dict):
            batch = extract_task_list(data.get("data"))
        if not batch:
            break
        out.extend(batch)
        if len(batch) < page_size:
            break
    return out


def wait_task(
    task_id: str,
    max_wait: int = 600,
    poll_interval: float = 5.0,
) -> dict[str, Any]:
    deadline = time.time() + max_wait
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = get_task(task_id)
        st = last.get("status") or ""
        if st in ("succeeded", "failed", "cancelled", "expired"):
            record_status(
                task_id,
                st,
                video_url=last.get("video_url"),
            )
            return last
        time.sleep(poll_interval)
    last["error"] = f"等待超时（{max_wait}s）"
    return last


# --- shots.yaml 提交（与天工 storyboard_submit_seedance 对齐）---


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("需要 PyYAML: pip3 install pyyaml")
        doc = yaml.safe_load(text)
    else:
        doc = json.loads(text)
    if not isinstance(doc, dict):
        raise RuntimeError("shots 文件根节点须为对象")
    return doc


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


def build_content_array(shot: dict, project_root: Path) -> list[dict]:
    api = shot.get("api") or {}
    content: list[dict] = [{"type": "text", "text": api.get("text", "")}]
    for role_spec in api.get("content_roles") or []:
        file_key = role_spec["file"]
        rel = role_file_to_path(shot, file_key)
        if not rel:
            raise ValueError(f"{shot.get('shot_id')}: 找不到素材 {file_key}")
        url = resolve_image_url(rel, project_root)
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": url},
                "role": role_spec["role"],
            }
        )
    return content


def build_shot_body(episode: dict, shot: dict, project_root: Path) -> dict[str, Any]:
    defaults = episode.get("defaults") or {}
    body: dict[str, Any] = {
        "model": defaults.get("model", default_model()),
        "content": build_content_array(shot, project_root),
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


def validate_shot_assets(shot: dict, project_root: Path) -> list[str]:
    missing = []
    assets = shot.get("assets") or {}
    paths: list[str] = []
    for key in ("first_frame", "last_frame"):
        if assets.get(key):
            paths.append(assets[key])
    for mapping in (assets.get("look_urls") or {}).values():
        paths.append(mapping)
    for mapping in (assets.get("scene_urls") or {}).values():
        paths.append(mapping)
    for rel in paths:
        p = project_root / rel if not Path(rel).is_absolute() else Path(rel)
        if not p.is_file():
            missing.append(str(rel))
    return missing


def cmd_docs(_: argparse.Namespace) -> int:
    import os

    doc = {
        "docs": [
            "https://www.volcengine.com/docs/82379/2291680?lang=zh",
            "https://www.volcengine.com/docs/82379/1393047?lang=zh",
            "https://www.volcengine.com/docs/82379/2222480?lang=zh",
        ],
        "create": base_url() + TASKS_PATH,
        "get": base_url() + TASKS_PATH + "/{task_id}",
        "list": base_url() + TASKS_PATH,
        "model_default": default_model(),
        "env": [
            "ARK_API_KEY",
            "ARK_BASE_URL",
            "ARK_SEEDANCE_MODEL",
            "ARK_PROJECT_ROOT",
        ],
        "archive_dir": get_archive_base_hint(),
        "note": "本地 assets 自动转 data URI 提交，无需图床；任务写入 video/ark_tasks/",
    }
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    project_root = (
        Path(args.project_root).expanduser().resolve() if args.project_root else None
    )
    if args.body_json:
        body = json.loads(Path(args.body_json).expanduser().read_text(encoding="utf-8"))
    else:
        if not args.text:
            print(json.dumps({"error": "需要 --text 或 --body-json"}, ensure_ascii=False))
            return 1
        images: list[tuple[str, str]] = []
        for spec in args.image_url or []:
            if ":" in spec and not spec.strip().startswith(("http:", "https:", "data:")):
                path_part, role = spec.rsplit(":", 1)
                images.append((path_part.strip(), role.strip()))
            else:
                images.append((spec.strip(), args.image_role or "reference_image"))
        body = {
            "model": args.model or default_model(),
            "content": build_content_from_simple(
                args.text, images or None, project_root
            ),
            "ratio": args.ratio or "9:16",
            "resolution": args.resolution or "720p",
            "duration": args.duration or 5,
            "generate_audio": args.generate_audio,
            "watermark": args.watermark,
        }
        if args.return_last_frame:
            body["return_last_frame"] = True
    result = create_task(body, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("submitted", "dry_run") else 1


def cmd_get(args: argparse.Namespace) -> int:
    print(json.dumps(get_task(args.task_id), ensure_ascii=False, indent=2))
    return 0


def cmd_archive_list(args: argparse.Namespace) -> int:
    tasks = list_local_tasks(args.limit, args.type)
    print(json.dumps({"archive_dir": get_archive_base_hint(), "tasks": tasks}, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    if args.local:
        return cmd_archive_list(args)
    if not api_key():
        print(json.dumps({"error": "未设置 ARK_API_KEY"}, ensure_ascii=False))
        return 1
    tasks = list_tasks(args.status, args.model, args.page_size, args.max_pages)
    if args.json:
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
        return 0
    for t in tasks:
        tid = str(t.get("id") or t.get("task_id") or "")
        st = task_status(t) or "?"
        vu = extract_video_url(t) or ""
        preview = (vu[:72] + "…") if len(vu) > 72 else vu
        print(f"{tid}\t{st}\t{t.get('model', '')}\t{preview}")
    return 0


def cmd_wait(args: argparse.Namespace) -> int:
    r = wait_task(args.task_id, args.max_wait, args.interval)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r.get("status") == "succeeded" else 1


def cmd_download(args: argparse.Namespace) -> int:
    url = args.url
    if not url and args.task_id:
        info = get_task(args.task_id)
        url = info.get("video_url")
        if not url and isinstance(info.get("task"), dict):
            url = extract_video_url(info["task"])
    if not url:
        print(json.dumps({"error": "无 video_url，请确认任务已成功"}, ensure_ascii=False))
        return 1
    out = args.output or safe_mp4_name(args.task_id or "seedance")
    r = download_url(url, out)
    if args.task_id:
        record_status(
            args.task_id,
            "succeeded",
            video_url=url,
            local_mp4=str(Path(out).resolve()),
        )
    print(json.dumps({"status": "ok", **r}, ensure_ascii=False, indent=2))
    return 0


def segment_file_to_path(segment: dict, file_key: str) -> str | None:
    assets = segment.get("assets") or {}
    looks = assets.get("look_urls") or {}
    if file_key in looks:
        return looks[file_key]
    scenes = assets.get("scene_urls") or {}
    if file_key in scenes:
        return scenes[file_key]
    voice_refs = segment.get("voice_refs") or {}
    if file_key in voice_refs:
        return voice_refs[file_key]
    return None


def validate_segment_assets(segment: dict, project_root: Path) -> list[str]:
    missing = []
    assets = segment.get("assets") or {}
    for mapping in (assets.get("look_urls") or {}).values():
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    for mapping in (assets.get("scene_urls") or {}).values():
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    for mapping in (segment.get("voice_refs") or {}).values():
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    return missing


def build_segment_content_array(segment: dict, project_root: Path) -> list[dict]:
    api = segment.get("api") or {}
    content: list[dict] = [{"type": "text", "text": (api.get("text") or "").strip()}]
    for role_spec in api.get("content_roles") or []:
        file_key = role_spec["file"]
        rel = segment_file_to_path(segment, file_key)
        if not rel:
            raise ValueError(f"{segment.get('segment_id')}: 找不到素材 {file_key}")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": resolve_image_url(rel, project_root)},
                "role": role_spec["role"],
            }
        )
    for _cid, rel in (segment.get("voice_refs") or {}).items():
        if rel:
            content.append(
                {
                    "type": "audio_url",
                    "audio_url": {"url": resolve_media_url(rel, project_root)},
                    "role": "reference_audio",
                }
            )
    return content


def _duration_bounds(model: str) -> tuple[int, int]:
    return (4, 12) if "fast" in model else (4, 15)


def _clamp_duration(sec: int, model: str) -> int:
    lo, hi = _duration_bounds(model)
    return max(lo, min(hi, int(sec)))


def build_segment_body(episode: dict, segment: dict, project_root: Path) -> dict[str, Any]:
    defaults = episode.get("defaults") or {}
    model = defaults.get("model", default_model())
    raw_dur = segment.get("duration_sec", defaults.get("duration", 5))
    body: dict[str, Any] = {
        "model": model,
        "content": build_segment_content_array(segment, project_root),
        "ratio": defaults.get("ratio", "9:16"),
        "resolution": defaults.get("resolution", "720p"),
        "duration": _clamp_duration(raw_dur, model),
        "generate_audio": defaults.get("generate_audio", True),
        "watermark": defaults.get("watermark", False),
    }
    api = segment.get("api") or {}
    if api.get("return_last_frame"):
        body["return_last_frame"] = True
    if api.get("seed") is not None:
        body["seed"] = api["seed"]
    return body


def cmd_segments(args: argparse.Namespace) -> int:
    ep_id = args.episode.upper()
    project_root = Path(args.project_root).expanduser().resolve()
    seg_path = (
        Path(args.segments_file).expanduser().resolve()
        if args.segments_file
        else project_root / "分集剧本" / f"{ep_id}_segments.yaml"
    )
    if not seg_path.is_file():
        print(json.dumps({"error": f"找不到 {seg_path}"}, ensure_ascii=False))
        return 1

    episode = load_yaml_or_json(seg_path)
    segments = episode.get("segments") or []
    if args.segment:
        segments = [s for s in segments if s.get("segment_id") == args.segment]
        if not segments:
            print(json.dumps({"error": f"未找到 {args.segment}"}, ensure_ascii=False))
            return 1

    results: list[dict[str, Any]] = []
    ready = 0

    for seg in segments:
        sid = seg.get("segment_id", "?")
        miss = validate_segment_assets(seg, project_root)
        if miss:
            results.append({"segment_id": sid, "status": "missing_assets", "missing": miss})
            if args.check_only:
                print(f"✗ {sid} 缺 {len(miss)} 个文件", file=sys.stderr)
            continue
        ready += 1
        if args.check_only:
            print(f"✓ {sid} 素材齐全", file=sys.stderr)
            continue
        try:
            body = build_segment_body(episode, seg, project_root)
            if args.dry_run:
                results.append(
                    {
                        "segment_id": sid,
                        "status": "dry_run",
                        "body": sanitize_body_for_log(body),
                    }
                )
                continue
            r = create_task(
                body,
                dry_run=False,
                archive_meta={
                    "segment_id": sid,
                    "episode": ep_id,
                    "project_root": str(project_root),
                    "project": project_root.name,
                },
            )
            r["segment_id"] = sid
            results.append(r)
            time.sleep(args.delay)
        except Exception as e:
            results.append({"segment_id": sid, "status": "error", "error": str(e)})

    summary = {
        "episode": ep_id,
        "ready": ready,
        "archive_dir": get_archive_base_hint(),
        "image_source": "local_data_uri",
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.check_only and any(r.get("status") == "missing_assets" for r in results):
        return 1
    if any(r.get("status") == "error" for r in results):
        return 1
    return 0


def cmd_shots(args: argparse.Namespace) -> int:
    import os

    ep_id = args.episode.upper()
    project_root = Path(args.project_root).expanduser().resolve()
    shots_path = (
        Path(args.shots_file).expanduser().resolve()
        if args.shots_file
        else project_root / "分集剧本" / f"{ep_id}_shots.yaml"
    )
    if not shots_path.is_file():
        alt = shots_path.with_suffix(".json")
        if alt.is_file():
            shots_path = alt
        else:
            print(json.dumps({"error": f"找不到 {shots_path}"}, ensure_ascii=False))
            return 1

    episode = load_yaml_or_json(shots_path)
    shots = episode.get("shots") or []
    if args.shot:
        shots = [s for s in shots if s.get("shot_id") == args.shot]
        if not shots:
            print(json.dumps({"error": f"未找到 {args.shot}"}, ensure_ascii=False))
            return 1

    results: list[dict[str, Any]] = []
    skipped = ready = 0

    for shot in shots:
        sid = shot.get("shot_id", "?")
        if shot.get("mode") == "skip":
            skipped += 1
            continue
        miss = validate_shot_assets(shot, project_root)
        if miss:
            results.append({"shot_id": sid, "status": "missing_assets", "missing": miss})
            if args.check_only:
                print(f"✗ {sid} 缺 {len(miss)} 个文件", file=sys.stderr)
            continue
        ready += 1
        if args.check_only:
            print(f"✓ {sid} 素材齐全", file=sys.stderr)
            continue
        try:
            body = build_shot_body(episode, shot, project_root)
            if args.dry_run:
                results.append(
                    {
                        "shot_id": sid,
                        "status": "dry_run",
                        "body": sanitize_body_for_log(body),
                    }
                )
                continue
            r = create_task(
                body,
                dry_run=False,
                archive_meta={
                    "shot_id": sid,
                    "episode": ep_id,
                    "project_root": str(project_root),
                    "project": project_root.name,
                },
            )
            r["shot_id"] = sid
            results.append(r)
            time.sleep(args.delay)
        except Exception as e:
            results.append({"shot_id": sid, "status": "error", "error": str(e)})

    summary = {
        "episode": ep_id,
        "skipped": skipped,
        "ready": ready,
        "archive_dir": get_archive_base_hint(),
        "image_source": "local_data_uri",
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.check_only and any(r.get("status") == "missing_assets" for r in results):
        return 1
    if any(r.get("status") == "error" for r in results):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="火山方舟 Seedance 2.0 视频 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_docs = sub.add_parser("docs")
    p_docs.set_defaults(func=cmd_docs)

    p_create = sub.add_parser("create", help="创建视频生成任务")
    p_create.add_argument("--body-json", help="完整请求体 JSON 文件")
    p_create.add_argument("--text", "-t", help="提示词（无 body-json 时）")
    p_create.add_argument(
        "--image-url",
        action="append",
        help="图片 URL；可写 url:role，如 https://...:first_frame",
    )
    p_create.add_argument("--image-role", default="reference_image")
    p_create.add_argument("--model", default=None)
    p_create.add_argument("--ratio", default="9:16")
    p_create.add_argument("--resolution", default="720p")
    p_create.add_argument("--duration", type=int, default=5)
    p_create.add_argument("--generate-audio", action="store_true")
    p_create.add_argument("--watermark", action="store_true")
    p_create.add_argument("--return-last-frame", action="store_true")
    p_create.add_argument("--dry-run", action="store_true")
    p_create.add_argument(
        "--project-root",
        help="本地图片路径相对根目录（默认可省略，仅路径为相对时）",
    )
    p_create.set_defaults(func=cmd_create)

    p_get = sub.add_parser("get")
    p_get.add_argument("--task-id", required=True)
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status")
    p_list.add_argument("--model")
    p_list.add_argument("--page-size", type=int, default=50)
    p_list.add_argument("--max-pages", type=int, default=5)
    p_list.add_argument("--json", action="store_true")
    p_list.add_argument(
        "--local",
        action="store_true",
        help="读本地归档 video/ark_tasks/ 而非方舟 API",
    )
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--type", choices=["image", "video"], help="--local 时筛选")
    p_list.set_defaults(func=cmd_list)

    p_wait = sub.add_parser("wait")
    p_wait.add_argument("--task-id", required=True)
    p_wait.add_argument("--max-wait", type=int, default=600)
    p_wait.add_argument("--interval", type=float, default=5.0)
    p_wait.set_defaults(func=cmd_wait)

    p_dl = sub.add_parser("download")
    p_dl.add_argument("--task-id")
    p_dl.add_argument("--url")
    p_dl.add_argument("--output", "-o")
    p_dl.set_defaults(func=cmd_download)

    p_shots = sub.add_parser("shots", help="从 EP##_shots.yaml 提交")
    p_shots.add_argument("episode", help="如 EP01")
    p_shots.add_argument("--project-root", required=True, help="短剧项目根，如 darams/天工开物")
    p_shots.add_argument("--shots-file", help="覆盖默认 分集剧本/EP##_shots.yaml")
    p_shots.add_argument(
        "--cdn-base",
        help="（已废弃，忽略）兼容旧参数；现用本地 data URI",
    )
    p_shots.add_argument("--shot", help="仅指定 shot_id")
    p_shots.add_argument("--check-only", action="store_true")
    p_shots.add_argument("--dry-run", action="store_true")
    p_shots.add_argument("--delay", type=float, default=0.5)
    p_shots.set_defaults(func=cmd_shots)

    p_seg = sub.add_parser("segments", help="从 EP##_segments.yaml 提交段落视频")
    p_seg.add_argument("episode", help="如 EP01")
    p_seg.add_argument("--project-root", required=True, help="短剧项目根，如 darams/天工开物")
    p_seg.add_argument("--segments-file", help="覆盖默认 分集剧本/EP##_segments.yaml")
    p_seg.add_argument("--segment", help="仅指定 segment_id")
    p_seg.add_argument("--check-only", action="store_true")
    p_seg.add_argument("--dry-run", action="store_true")
    p_seg.add_argument("--delay", type=float, default=0.5)
    p_seg.set_defaults(func=cmd_segments)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
