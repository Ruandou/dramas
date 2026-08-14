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
import uuid
from pathlib import Path
from typing import Any

# 公共基建层 mcps/shared（本项目脚本从 mcps/shared/ 直接运行时无需此段）
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from archive import list_tasks as list_local_tasks
from project_task_archive import KIND_SEEDANCE, assert_valid_drama_project_root
import dedup
import engine_registry
from ark_seedance_record import (
    record_status,
    record_submit,
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
from media_utils import load_cdn_registry, lookup_tos_url, resolve_image_url, resolve_media_url

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

DEFAULT_MODEL = "doubao-seedance-2-0-fast-260128"
DEFAULT_ENDPOINT_SUFFIX = TASKS_PATH

# 缺版本后缀的模型名会被方舟以 HTTP 404 InvalidEndpointOrModel.NotFound 拒绝（不建单不扣费）。
# 历史上大量 YAML/模板把无后缀名写进 defaults.model，这里做统一规范化兜底，
# 任何来源（YAML defaults / --model / 环境变量）的模型名都经过 normalize_model()。
MODEL_ALIASES = {
    "doubao-seedance-2-0-fast": "doubao-seedance-2-0-fast-260128",
    "doubao-seedance-2-0": "doubao-seedance-2-0-260128",
}


def normalize_model(name: str | None) -> str:
    """模型名规范化：已知无后缀别名自动补齐并告知；未知无后缀 doubao-seed* 名称告警。"""
    import re

    name = (name or "").strip()
    if not name:
        return default_model()
    if name in MODEL_ALIASES:
        fixed = MODEL_ALIASES[name]
        print(f"⚠️ 模型名 '{name}' 缺版本后缀，已自动规范化为 '{fixed}'（请修正 YAML 源头）", file=sys.stderr)
        return fixed
    if name.startswith("doubao-seed") and not re.search(r"-\d{6}$", name):
        print(f"⚠️ 模型名 '{name}' 疑似缺版本后缀（如 -260128），方舟可能返回 404", file=sys.stderr)
    return name


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
    # 先算内容指纹写 submitting 卡位（POST 之前落盘）—— 网络抖动时方舟可能已建单，
    # 本地却没拿到 response；下次对账会看到卡位，走远程幂等回写而非盲重发。
    client_request_id = f"local-{uuid.uuid4()}"
    # 指纹优先用 archive_meta["fingerprint"]（cmd 循环已按 build_segment 同样 default 算好），
    # 保证循环对账与归档写入用绝对同一字符串，不依赖两条 default 解析路径会一直对齐。
    fingerprint = str(archive_meta.get("fingerprint") or "") if archive_meta else ""
    placeholder_id = client_request_id
    identity_key = ""
    if archive_meta:
        proot = archive_meta.get("project_root")
        identity_key = archive_meta.get("segment_id") or archive_meta.get("shot_id") or ""
        if proot and identity_key:
            try:
                if not fingerprint:
                    fingerprint = dedup.fingerprint_video(
                    prompt=_segment_text_from_body(body),
                    model=body.get("model"),
                    duration=body.get("duration"),
                    ratio=body.get("ratio"),
                    resolution=body.get("resolution"),
                    media_urls=_segment_media_urls_from_body(body),
                )
                dedup.add_submitting_placeholder(
                    proot,
                    kind=KIND_SEEDANCE,
                    episode_id=archive_meta.get("episode"),
                    client_request_id=client_request_id,
                    fingerprint=fingerprint,
                    identity_key=identity_key,
                    extra_params={
                        "segment_id": archive_meta.get("segment_id"),
                        "shot_id": archive_meta.get("shot_id"),
                        "project": archive_meta.get("project") or "天工开物",
                    },
                )
            except Exception as e:
                # 归档写失败：API 可能仍会建单，绝不让 agent 闷头重发——转交上层兜底
                print(
                    f"⚠️ 归档写卡位失败但即将继续 POST，方舟可能已扣费：{e}",
                    file=sys.stderr,
                )
    resp = http_request("POST", TASKS_PATH, body=body, timeout=180)
    tid = task_id_from_response(resp)
    if tid and archive_meta:
        proot = archive_meta.get("project_root")
        if proot:
            #提拔 submitting 卡位 → 写入真实 task_id
            try:
                dedup.promote_submitting(
                    proot,
                    kind=KIND_SEEDANCE,
                    episode_id=archive_meta.get("episode"),
                    client_request_id=placeholder_id,
                    real_task_id=tid,
                    extra_updates={
                        "fingerprint": fingerprint,
                        "segment_id": archive_meta.get("segment_id"),
                        "shot_id": archive_meta.get("shot_id"),
                        "project": archive_meta.get("project") or "天工开物",
                        "episode": str(archive_meta.get("episode") or "").upper(),
                    },
                )
            except Exception:
                # 兜底走老路径，保证至少有 submitted 条目
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


def _segment_text_from_body(body: dict) -> str:
    content = body.get("content") or []
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(str(item.get("text") or ""))
        return "\n".join(texts)
    return str(body.get("text") or body.get("prompt") or "")


def _segment_media_urls_from_body(body: dict) -> list[str]:
    urls: list[str] = []
    for item in body.get("content") or []:
        if isinstance(item, dict):
            iu = item.get("image_url") or item.get("audio_url") or {}
            if isinstance(iu, dict) and iu.get("url"):
                urls.append(str(iu["url"]))
    return sorted(set(urls))


def get_archive_base_hint() -> str:
    from archive import get_archive_base

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
    props = assets.get("prop_urls") or {}
    if file_key in props:
        return props[file_key]
    return None


def build_content_array(shot: dict, project_root: Path,
                        prompt_suffix: str | None = None,
                        prompt_suffix_silent: str | None = None) -> list[dict]:
    api = shot.get("api") or {}
    # 结构化 api 块（subjects/shots）→ 按 Seedance 旧【图N】格式渲染；无结构化块回退 api.text
    try:
        from prompt_renderer import render as _render_prompt
        text = _render_prompt("seedance", api, prompt_suffix=prompt_suffix,
                              prompt_suffix_silent=prompt_suffix_silent)
    except Exception as e:
        # 渲染器异常不应静默：回退 api.text 但报警，避免掩盖渲染 bug
        print(f"⚠️ prompt_renderer 渲染失败，回退 api.text：{e}", file=sys.stderr)
        text = api.get("text", "")
    content: list[dict] = [{"type": "text", "text": text}]
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
        "model": normalize_model(defaults.get("model") or default_model()),
        "content": build_content_array(shot, project_root,
                                        prompt_suffix=defaults.get("prompt_suffix"),
                                        prompt_suffix_silent=defaults.get("prompt_suffix_silent")),
        "ratio": engine_registry.normalize_ratio(defaults.get("ratio", "9:16")),
        "resolution": defaults.get("resolution", "720p"),
        "duration": shot.get("duration_sec", defaults.get("duration", 5)),
        "generate_audio": defaults.get("generate_audio", False),
        "watermark": defaults.get("watermark", False),
    }
    if defaults.get("seed") is not None:
        body["seed"] = defaults["seed"]
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
    for mapping in (assets.get("prop_urls") or {}).values():
        paths.append(mapping)
    for rel in paths:
        if rel.startswith(("http://", "https://", "data:")):
            continue  # remote URL — no local file check needed
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
        if isinstance(body, dict) and body.get("model"):
            body["model"] = normalize_model(body["model"])
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
            "model": normalize_model(args.model or default_model()),
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
    result = create_task(
        body,
        dry_run=args.dry_run,
        archive_meta={
            "episode": str(args.episode or ""),
            "project_root": str(project_root) if project_root else "",
            "project": project_root.name if project_root else "",
        } if project_root else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("submitted", "dry_run") else 1


def cmd_get(args: argparse.Namespace) -> int:
    # 先查本地归档状态：若任务还在 pending/running/submitting，提前打 cancel 语义提示，
    # 避免无 ARK_API_KEY 或 API 失败时 agent 误以为"取消有效"。
    import os
    if getattr(args, "project_root", None):
        try:
            project_root = assert_valid_drama_project_root(args.project_root)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
        os.environ.setdefault("DRAMA_PROJECT_ROOT", str(project_root))
    local_status = None
    try:
        for t in list_local_tasks(limit=500):
            if str(t.get("task_id", "")) == str(args.task_id):
                local_status = (t.get("status") or "").lower()
                break
    except Exception:
        local_status = None
    pending_locals = ("pending", "running", "queued", "in_progress", "submitting")
    if local_status in pending_locals:
        print(
            "⚠️ 方舟不支持撤回已建单任务，'取消'仅能丢弃本地跟踪，任务仍计费至完成。"
            "如需等待结果用 wait；如担心重复扣费，下次先用 --status / reconcile 核对。",
            file=sys.stderr,
        )
    try:
        info = get_task(args.task_id)
    except Exception as e:
        if local_status in pending_locals:
            print(json.dumps(
                {"task_id": args.task_id, "local_status": local_status, "error": str(e)},
                ensure_ascii=False, indent=2))
            return 1
        raise
    st = (info.get("status") or "").lower()
    if st in pending_locals:
        print(
            "⚠️ 方舟不支持撤回已建单任务，'取消'仅能丢弃本地跟踪，任务仍计费至完成。"
            "如需等待结果用 wait；如担心重复扣费，下次先用 --status / reconcile 核对。",
            file=sys.stderr,
        )
    print(json.dumps(info, ensure_ascii=False, indent=2))
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
    props = assets.get("prop_urls") or {}
    if file_key in props:
        return props[file_key]
    voice_refs = segment.get("voice_refs") or {}
    if file_key in voice_refs:
        return voice_refs[file_key]
    return None


def validate_segment_assets(segment: dict, project_root: Path) -> list[str]:
    missing = []
    assets = segment.get("assets") or {}
    for mapping in (assets.get("look_urls") or {}).values():
        if mapping.startswith(("http://", "https://", "data:")):
            continue  # remote URL — no local file check needed
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    for mapping in (assets.get("scene_urls") or {}).values():
        if mapping.startswith(("http://", "https://", "data:")):
            continue
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    for mapping in (assets.get("prop_urls") or {}).values():
        if mapping.startswith(("http://", "https://", "data:")):
            continue
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    for mapping in (segment.get("voice_refs") or {}).values():
        if mapping.startswith(("http://", "https://", "data:")):
            continue
        p = project_root / mapping if not Path(mapping).is_absolute() else Path(mapping)
        if not p.is_file():
            missing.append(str(mapping))
    return missing


def build_segment_content_array(
    segment: dict,
    project_root: Path,
    cdn_registry: dict | None = None,
    prompt_suffix: str | None = None,
    prompt_suffix_silent: str | None = None,
) -> list[dict]:
    api = segment.get("api") or {}
    # 结构化 api 块（subjects/shots）→ 按 Seedance 旧【图N】格式渲染；无结构化块回退 api.text
    try:
        from prompt_renderer import render as _render_prompt
        text = _render_prompt("seedance", api, prompt_suffix=prompt_suffix,
                              prompt_suffix_silent=prompt_suffix_silent)
    except Exception as e:
        # 渲染器异常不应静默：回退 api.text 但报警，避免掩盖渲染 bug
        print(f"⚠️ prompt_renderer 渲染失败，回退 api.text：{e}", file=sys.stderr)
        text = (api.get("text") or "").strip()
    content: list[dict] = [{"type": "text", "text": text}]
    for role_spec in api.get("content_roles") or []:
        file_key = role_spec["file"]
        # TOS URL lookup: use permanent HTTPS URL if available
        tos_url = lookup_tos_url(file_key, cdn_registry)
        if tos_url:
            url = tos_url
        else:
            rel = segment_file_to_path(segment, file_key)
            if not rel:
                raise ValueError(f"{segment.get('segment_id')}: 找不到素材 {file_key}")
            url = resolve_image_url(rel, project_root)
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": url},
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


def build_segment_body(
    episode: dict,
    segment: dict,
    project_root: Path,
    cdn_registry: dict | None = None,
) -> dict[str, Any]:
    defaults = episode.get("defaults") or {}
    model = normalize_model(defaults.get("model") or default_model())
    raw_dur = segment.get("duration_sec", defaults.get("duration", 5))
    body: dict[str, Any] = {
        "model": model,
        "content": build_segment_content_array(segment, project_root, cdn_registry,
                                                 prompt_suffix=defaults.get("prompt_suffix"),
                                                 prompt_suffix_silent=defaults.get("prompt_suffix_silent")),
        "ratio": engine_registry.normalize_ratio(defaults.get("ratio", "9:16")),
        "resolution": defaults.get("resolution", "720p"),
        "duration": _clamp_duration(raw_dur, model),
        "generate_audio": defaults.get("generate_audio", True),
        "watermark": defaults.get("watermark", False),
    }
    api = segment.get("api") or {}
    if api.get("return_last_frame"):
        body["return_last_frame"] = True
    # 音色/节奏稳定：官方推荐「固定 seed + 详细声音描述」（SD2.0_音色参考不准导致漂移的解法 Tip1）。
    # 段级 api.seed 优先，其次 defaults.seed（全集统一）；都未设则随机。
    if api.get("seed") is not None:
        body["seed"] = api["seed"]
    elif defaults.get("seed") is not None:
        body["seed"] = defaults["seed"]
    return body


def _segment_fingerprint(seg: dict, episode: dict) -> str:
    """从 segment 字典算视频内容指纹（prompt/时長/素材图等）。"""
    try:
        return dedup.fingerprint_segment(seg, model=episode.get("model") or default_model())
    except Exception:
        # 解析失败不应阻塞提交；返回空让对账退化为本地 identity 去重
        return ""


def _segment_status_label(sid: str, fp: str, project_root: Path, ep_id: str, remote_index: dict | None) -> str:
    """生成 ✅submitted / ⏳submitting / ❓not_submitted 标签。"""
    local = dedup.local_lookup(
        project_root, kind=KIND_SEEDANCE, episode_id=ep_id,
        identity_key=sid, fingerprint=fp,
    )
    if local.get("matched") and local.get("kind") == "submitted":
        return f"✅submitted(task_id={local['existing_task'].get('task_id')})"
    if local.get("matched") and local.get("kind") == "submitting":
        return f"⏳submitting({'stale' if local.get('stale') else 'in_progress'})"
    if remote_index is not None and fp and fp in remote_index:
        return f"✅submitted_remote(task_id={remote_index[fp]['remote_task_id']})"
    return "❓not_submitted"


def _shot_fingerprint(shot: dict, episode: dict) -> str:
    """shot 与 segment 结构同构，复用 fingerprint_segment（identity 字段为 shot_id）。"""
    # 把 shot 当 segment 算；content 字段名一致
    try:
        return dedup.fingerprint_segment(shot, model=episode.get("model") or default_model())
    except Exception:
        return ""


def _shot_status_label(sid: str, fp: str, project_root: Path, ep_id: str, remote_index: dict | None) -> str:
    """shots 的 ✅submitted / ⏳submitting / ❓not_submitted 状态标签。"""
    local = dedup.local_lookup(
        project_root, kind=KIND_SEEDANCE, episode_id=ep_id,
        identity_key=sid, fingerprint=fp,
    )
    if local.get("matched") and local.get("kind") == "submitted":
        return f"✅submitted(task_id={local['existing_task'].get('task_id')})"
    if local.get("matched") and local.get("kind") == "submitting":
        return f"⏳submitting({'stale' if local.get('stale') else 'in_progress'})"
    if remote_index is not None and fp and fp in remote_index:
        return f"✅submitted_remote(task_id={remote_index[fp]['remote_task_id']})"
    return "❓not_submitted"


def _coordination_block(
    *,
    project_root: Path,
    ep_id: str,
    args: argparse.Namespace,
) -> dict[str, dict] | None:
    """segments 与 shots 共用的对账前置。返回 remote_index 或 None；也处理 force 二次确认。

    remote_index 为 {fingerprint: {remote_task_id, remote_task}}，供循环内本地未命中时查远程。
    网络/无 key 失败时返回 None（退回本地去重），不抛错。"""
    ok_force, force_msg = dedup.require_force_confirm(args.force)
    if args.force and not ok_force:
        print(force_msg, file=sys.stderr)
        args.force = False

    remote_index: dict[str, dict] | None = None
    do_remote = (getattr(args, "check_remote", False) or getattr(args, "pending", False) or getattr(args, "status", False)) and not getattr(args, "no_remote", False)
    if not getattr(args, "force", False) and do_remote:
        try:
            remote_tasks = list_tasks(model=default_model(), page_size=100, max_pages=6)
            remote_index = {}
            for rt in remote_tasks:
                fp = dedup.remote_fingerprint_from_task(rt)
                if fp and fp not in remote_index:
                    tid = rt.get("id") or rt.get("task_id")
                    remote_index[fp] = {"remote_task_id": tid, "remote_task": rt}
            if remote_index:
                print(f"✓ Remote reconcile: {len(remote_index)} recent tasks", file=sys.stderr)
        except Exception as e:
            print(f"⚠ Remote check failed (non-blocking, 退回本地去重): {e}", file=sys.stderr)
    return remote_index


def cmd_segments(args: argparse.Namespace) -> int:
    ep_id = args.episode.upper()
    try:
        project_root = assert_valid_drama_project_root(args.project_root)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
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

    # Load CDN registry for TOS URL resolution (tos_first strategy)
    cdn_registry: dict | None = None
    registry_config = episode.get("image_cdn_registry")
    if registry_config and isinstance(registry_config, dict):
        cdn_registry = load_cdn_registry(registry_config, project_root)
        if cdn_registry:
            print(
                f"✓ CDN registry loaded: {len(cdn_registry)} assets with TOS URLs",
                file=sys.stderr,
            )

    # force 二次确认：挡 agent 随手 --force 重复扣费
    ok_force, force_msg = dedup.require_force_confirm(args.force)
    if args.force and not ok_force:
        print(force_msg, file=sys.stderr)
        args.force = False

    # --- Dedup（本地指纹 + 远程对账 + submitting 卡位兜底）---
    # 计算 segment 指纹以便本地+远程核对（--status / --pending 用同一份）
    seg_fp: dict[str, str] = {}
    for seg in segments:
        seg_fp[seg.get("segment_id", "?")] = _segment_fingerprint(seg, episode)

    remote_index: dict[str, dict] | None = None  # {fingerprint: remote hit}
    if not args.force and (args.check_remote or args.pending or args.status):
        do_remote = not getattr(args, "no_remote", False)
        if do_remote:
            try:
                remote_tasks = list_tasks(model=default_model(), page_size=100, max_pages=6)
                remote_index = {}
                for rt in remote_tasks:
                    fp = dedup.remote_fingerprint_from_task(rt)
                    if fp and fp not in remote_index:
                        tid = rt.get("id") or rt.get("task_id")
                        remote_index[fp] = {"remote_task_id": tid, "remote_task": rt}
                if remote_index:
                    print(
                        f"✓ Remote reconcile: {len(remote_index)} recent tasks for this model",
                        file=sys.stderr,
                    )
            except Exception as e:
                print(f"⚠ Remote check failed (non-blocking, 退回本地去重): {e}", file=sys.stderr)

    results: list[dict[str, Any]] = []
    ready = 0

    # --status：只打印每段状态，不提交
    if getattr(args, "status", False):
        for seg in segments:
            sid = seg.get("segment_id", "?")
            st = _segment_status_label(sid, seg_fp.get(sid, ""), project_root, ep_id, remote_index)
            print(st, file=sys.stderr)
            results.append({"segment_id": sid, "status": st})
        print(json.dumps({"episode": ep_id, "results": results}, ensure_ascii=False, indent=2))
        return 0

    for seg in segments:
        sid = seg.get("segment_id", "?")
        fp = seg_fp.get(sid, "")
        # --- 对账：本地指纹 → 远程指纹 → submitting 卡位 ---
        if not args.force:
            local = dedup.local_lookup(
                project_root, kind=KIND_SEEDANCE, episode_id=ep_id,
                identity_key=sid, fingerprint=fp,
            )
            if local.get("matched") and local.get("kind") == "submitted":
                et = local["existing_task"].get("task_id")
                results.append({"segment_id": sid, "status": "already_submitted", "existing_task_id": et})
                print(f"⊙ {sid} 本地命中已提交 (task_id={et})，skip", file=sys.stderr)
                continue
            if local.get("matched") and local.get("kind") == "submitting":
                if local.get("stale") and remote_index is not None:
                    # 视频可远程幂等回写：找同 fingerprint 远程任务认领
                    hit = remote_index.get(fp)
                    if hit:
                        rtid = hit["remote_task_id"]
                        try:
                            dedup.write_back_remote(
                                project_root, episode_id=ep_id, remote_task_id=rtid,
                                fingerprint=fp, identity_key=sid,
                                extra_params={"segment_id": sid, "project": project_root.name},
                            )
                        except Exception:
                            pass
                        results.append({"segment_id": sid, "status": "reconciled_from_remote", "existing_task_id": rtid})
                        print(f"⊙ {sid} submitting 卡位 stale，远程认领 task_id={rtid}，skip", file=sys.stderr)
                        continue
                # 非 stale 的 submitting 或无远程对账 → 拦下不盲重发
                results.append({"segment_id": sid, "status": "submitting_blocked", "reason": "本地 submitting 卡位未结算，可能方舟已建单"})
                print(
                    f"⛔ {sid} 本地 submitting 卡位未结算（可能方舟已扣费）。"
                    f"如确认原请求未真发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
                    file=sys.stderr,
                )
                continue
            # 本地未命中 → 查远程
            if remote_index is not None:
                hit = remote_index.get(fp)
                if hit:
                    rtid = hit["remote_task_id"]
                    try:
                        dedup.write_back_remote(
                            project_root, episode_id=ep_id, remote_task_id=rtid,
                            fingerprint=fp, identity_key=sid,
                            extra_params={"segment_id": sid, "project": project_root.name},
                        )
                    except Exception:
                        pass
                    results.append({"segment_id": sid, "status": "reconciled_from_remote", "existing_task_id": rtid})
                    print(f"⊙ {sid} 远程命中已提交 (task_id={rtid})，补归档并 skip", file=sys.stderr)
                    continue
        # With TOS URLs, skip local file validation for assets that have TOS entries
        miss = validate_segment_assets(seg, project_root)
        if miss and cdn_registry:
            # Filter out missing files that have TOS URLs available
            still_missing = [
                m for m in miss
                if not lookup_tos_url(Path(m).stem, cdn_registry)
            ]
            miss = still_missing
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
            body = build_segment_body(episode, seg, project_root, cdn_registry)
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
                    "fingerprint": fp,
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
        "image_source": "tos_url" if cdn_registry else "local_data_uri",
        "cdn_assets": len(cdn_registry) if cdn_registry else 0,
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
    try:
        project_root = assert_valid_drama_project_root(args.project_root)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    ep_id = args.episode.upper()
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

    # --- 对账（本地指纹 + 远程对账 + submitting 卡位兜底）---
    shot_fp = {shot.get("shot_id", "?"): _shot_fingerprint(shot, episode) for shot in shots}
    remote_index = _coordination_block(project_root=project_root, ep_id=ep_id, args=args)

    results: list[dict[str, Any]] = []
    skipped = ready = 0

    # --status：只打印每个 shot 状态，绝不提交（防 --status 误发 POST 扣费）
    if getattr(args, "status", False):
        for shot in shots:
            sid = shot.get("shot_id", "?")
            st = _shot_status_label(sid, shot_fp.get(sid, ""), project_root, ep_id, remote_index)
            print(st, file=sys.stderr)
            results.append({"shot_id": sid, "status": st})
        print(json.dumps({"episode": ep_id, "results": results}, ensure_ascii=False, indent=2))
        return 0

    for shot in shots:
        sid = shot.get("shot_id", "?")
        fp = shot_fp.get(sid, "")
        # --- 对账 ---
        if not args.force:
            local = dedup.local_lookup(
                project_root, kind=KIND_SEEDANCE, episode_id=ep_id,
                identity_key=sid, fingerprint=fp,
            )
            if local.get("matched") and local.get("kind") == "submitted":
                et = local["existing_task"].get("task_id")
                results.append({"shot_id": sid, "status": "already_submitted", "existing_task_id": et})
                print(f"⊙ {sid} 本地命中已提交 (task_id={et})，skip", file=sys.stderr)
                continue
            if local.get("matched") and local.get("kind") == "submitting":
                if local.get("stale") and remote_index is not None:
                    hit = remote_index.get(fp)
                    if hit:
                        rtid = hit["remote_task_id"]
                        try:
                            dedup.write_back_remote(
                                project_root, episode_id=ep_id, remote_task_id=rtid,
                                fingerprint=fp, identity_key=sid,
                                extra_params={"shot_id": sid, "project": project_root.name},
                            )
                        except Exception:
                            pass
                        results.append({"shot_id": sid, "status": "reconciled_from_remote", "existing_task_id": rtid})
                        print(f"⊙ {sid} submitting 卡位 stale，远程认领 task_id={rtid}，skip", file=sys.stderr)
                        continue
                results.append({"shot_id": sid, "status": "submitting_blocked", "reason": "本地 submitting 卡位未结算"})
                print(
                    f"⛔ {sid} 本地 submitting 卡位未结算（可能方舟已扣费）。"
                    f"如确认原请求未真发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
                    file=sys.stderr,
                )
                continue
            if remote_index is not None and fp and fp in remote_index:
                hit = remote_index[fp]
                rtid = hit["remote_task_id"]
                try:
                    dedup.write_back_remote(
                        project_root, episode_id=ep_id, remote_task_id=rtid,
                        fingerprint=fp, identity_key=sid,
                        extra_params={"shot_id": sid, "project": project_root.name},
                    )
                except Exception:
                    pass
                results.append({"shot_id": sid, "status": "reconciled_from_remote", "existing_task_id": rtid})
                print(f"⊙ {sid} 远程命中已提交 (task_id={rtid})，补归档并 skip", file=sys.stderr)
                continue
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
                    "fingerprint": shot_fp.get(sid, ""),
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


def cmd_reconcile(args: argparse.Namespace) -> int:
    """拉近 7 天远程任务，按指纹把"丢的归档"写回本地 tasks.json。

    给 agent 一个标准动作替代"感觉失败了就重发"：先 reconcile 看哪些远程已存在、哪些可安全重发。"""
    try:
        project_root = assert_valid_drama_project_root(args.project_root)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    ep_id = args.episode.upper()
    seg_path = (
        Path(args.segments_file).expanduser().resolve()
        if args.segments_file
        else project_root / "分集剧本" / f"{ep_id}_segments.yaml"
    )

    # 拉远程
    try:
        remote_tasks = list_tasks(model=default_model(), page_size=100, max_pages=6)
    except Exception as e:
        print(json.dumps({"error": f"远程任务拉取失败：{e}"}, ensure_ascii=False))
        return 1
    remote_index: dict[str, dict] = {}
    for rt in remote_tasks:
        fp = dedup.remote_fingerprint_from_task(rt)
        if fp and fp not in remote_index:
            remote_index[fp] = {"remote_task_id": rt.get("id") or rt.get("task_id"), "remote_task": rt}

    results: list[dict[str, Any]] = []
    if seg_path.is_file():
        episode = load_yaml_or_json(seg_path)
        for seg in episode.get("segments") or []:
            sid = seg.get("segment_id", "?")
            fp = _segment_fingerprint(seg, episode)
            local = dedup.local_lookup(
                project_root, kind=KIND_SEEDANCE, episode_id=ep_id,
                identity_key=sid, fingerprint=fp,
            )
            if local.get("matched") and local.get("kind") == "submitted":
                results.append({"segment_id": sid, "status": "local_ok", "task_id": local["existing_task"].get("task_id")})
                continue
            hit = remote_index.get(fp)
            if hit:
                rtid = hit["remote_task_id"]
                try:
                    dedup.write_back_remote(
                        project_root, episode_id=ep_id, remote_task_id=rtid,
                        fingerprint=fp, identity_key=sid,
                        extra_params={"segment_id": sid, "project": project_root.name},
                    )
                except Exception as e:
                    results.append({"segment_id": sid, "status": "write_back_failed", "error": str(e)})
                    continue
                results.append({"segment_id": sid, "status": "reconciled_from_remote", "task_id": rtid})
                print(f"⊙ {sid} 远程命中 task_id={rtid}，已回写本地归档", file=sys.stderr)
            else:
                results.append({"segment_id": sid, "status": "remote_not_found", "note": "可安全重发（或排除网络原因）"})
    else:
        # 不指定 yaml：只把远程存在但本地缺的任务整体回写
        idx = dedup.read_local_index(project_root, kind=KIND_SEEDANCE, episode_id=ep_id)
        existing_ids = {_fp(t) for t in idx.values()}
        for fp, hit in remote_index.items():
            if hit["remote_task_id"] in existing_ids:
                continue
            try:
                dedup.write_back_remote(
                    project_root, episode_id=ep_id, remote_task_id=hit["remote_task_id"],
                    fingerprint=fp, identity_key="(reconciled)",
                    extra_params={"project": project_root.name},
                )
                results.append({"status": "reconciled_from_remote", "task_id": hit["remote_task_id"]})
            except Exception as e:
                results.append({"status": "write_back_failed", "error": str(e)})

    print(json.dumps({"episode": ep_id, "remote_count": len(remote_index), "results": results}, ensure_ascii=False, indent=2))
    return 0


def _fp(t: dict) -> str:
    """reconcile 内部：取 task_id 作现有集合去重用。"""
    return str(t.get("task_id") or "")


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
    p_create.add_argument(
        "--episode",
        default="",
        help="集数标记，如 EP01（写入 tasks.json 时用）",
    )
    p_create.set_defaults(func=cmd_create)

    p_get = sub.add_parser("get")
    p_get.add_argument("--task-id", required=True)
    p_get.add_argument("--project-root", help="短剧项目根，用于查本地归档状态提示 cancel 语义")
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

    p_rec = sub.add_parser("reconcile", help="拉近 7 天远程任务按指纹回写本地归档")
    p_rec.add_argument("episode", help="如 EP01")
    p_rec.add_argument("--project-root", required=True, help="短剧项目根，如 dramas/天工开物")
    p_rec.add_argument("--segments-file", help="基于 segments yaml 算指纹；不指定则仅回写远程存在但本地缺的")
    p_rec.set_defaults(func=cmd_reconcile)

    p_shots = sub.add_parser("shots", help="从 EP##_shots.yaml 提交")
    p_shots.add_argument("episode", help="如 EP01")
    p_shots.add_argument("--project-root", required=True, help="短剧项目根，如 dramas/天工开物")
    p_shots.add_argument("--shots-file", help="覆盖默认 分集剧本/EP##_shots.yaml")
    p_shots.add_argument(
        "--cdn-base",
        help="（已废弃，忽略）兼容旧参数；现用本地 data URI",
    )
    p_shots.add_argument("--shot", help="仅指定 shot_id")
    p_shots.add_argument("--check-only", action="store_true")
    p_shots.add_argument("--dry-run", action="store_true")
    p_shots.add_argument("--delay", type=float, default=0.5)
    p_shots.add_argument("--force", action="store_true", help="忽略去重检查，强制重新提交（需 ARK_ALLOW_FORCE=1）")
    p_shots.add_argument("--check-remote", action="store_true", help="额外查询云端任务列表进行去重")
    p_shots.add_argument("--no-remote", action="store_true", help="跳过远程对账，仅本地去重")
    p_shots.add_argument("--pending", action="store_true", help="只提交未提交的 shot（增量）")
    p_shots.add_argument("--status", action="store_true", help="只打印每个 shot 状态，不提交")
    p_shots.set_defaults(func=cmd_shots)

    p_seg = sub.add_parser("segments", help="从 EP##_segments.yaml 提交段落视频")
    p_seg.add_argument("episode", help="如 EP01")
    p_seg.add_argument("--project-root", required=True, help="短剧项目根，如 dramas/天工开物")
    p_seg.add_argument("--segments-file", help="覆盖默认 分集剧本/EP##_segments.yaml")
    p_seg.add_argument("--segment", help="仅指定 segment_id")
    p_seg.add_argument("--check-only", action="store_true")
    p_seg.add_argument("--dry-run", action="store_true")
    p_seg.add_argument("--delay", type=float, default=0.5)
    p_seg.add_argument("--force", action="store_true", help="忽略去重检查，强制重新提交")
    p_seg.add_argument(
        "--check-remote",
        action="store_true",
        help="额外查询云端任务列表进行去重（较慢但更全面）",
    )
    p_seg.add_argument("--no-remote", action="store_true", help="跳过远程对账，仅本地去重")
    p_seg.add_argument("--pending", action="store_true", help="只提交未提交的 segment（增量；与 --status 互补）")
    p_seg.add_argument("--status", action="store_true", help="只打印每段状态，不提交（dry-run 状态查询）")
    p_seg.set_defaults(func=cmd_segments)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
