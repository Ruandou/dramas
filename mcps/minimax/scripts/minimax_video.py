#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax-H3 视频生成 CLI（V2 多模态接口，异步任务）

文档：
  - 指南：https://platform.minimaxi.com/docs/guides/video-generation
  - 创建：https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create
  - 查询：https://platform.minimaxi.com/docs/api-reference/video-generation-v2-query

鉴权：Authorization: Bearer MINIMAX_API_KEY
接口：
  POST   /v2/video_generation               创建视频生成任务（返回 task_id）
  GET    /v2/query/video_generation/{id}    查询任务状态/成片 URL（7 天窗口）
  GET    /v2/query/video_generation         分页任务列表（7 天窗口）
  DELETE /v2/video_generation/{id}          取消 queued 任务 / 删除记录

规格要点：
  - duration 整数 4~15s（段级，段内多镜由 prompt「镜头1…镜头2…」驱动）
  - resolution: 768P / 2K；ratio: 9:16（i2va 时被忽略，由输入图决定；本流水线参考图即 9:16）
  - content[]: text 必填 + image_url（role: reference_image / first_frame / last_frame）
  - 人脸参考图是否触发涉敏（1026/1027）需实测；mesh 版 look 是否必要以实测为准
  - 任务记录仅保留 7 天，成片 URL 限时；提交后本地归档 + 及时下载

⚠️ 与 seedance 的差异（远程对账）：
  MiniMax list/query 不返回提交时的 prompt/参考图（content 仅有输出 url），
  无法按内容指纹做远程匹配 → --check-remote/reconcile 仅做 task_id 级整体回写；
  防重复扣费以本地指纹（dedup.local_lookup）为主防线。

CLI：
  python3 minimax_video.py docs
  python3 minimax_video.py create --text "..." --image-url https://...:reference_image --duration 5
  python3 minimax_video.py get --task-id 424010985738629
  python3 minimax_video.py list --status succeeded
  python3 minimax_video.py wait --task-id xxx
  python3 minimax_video.py download --task-id xxx -o out.mp4
  python3 minimax_video.py shots EP01 --project-root dramas/<剧名> --dry-run
  python3 minimax_video.py segments EP01 --project-root dramas/<剧名> --dry-run
  python3 minimax_video.py reconcile EP01 --project-root dramas/<剧名>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import requests

# 公共基建层 mcps/shared
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

import dedup
from media_utils import (
    load_cdn_registry,
    lookup_tos_url,
    resolve_image_url,
)
from project_task_archive import (
    KIND_MINIMAX,
    add_task,
    archive_file,
    assert_valid_drama_project_root,
    load_doc,
    save_doc,
    update_task,
)

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

BASE_URL = os.environ.get("MINIMAX_API_BASE", "https://metaso.cn/api/minimax")  # metaso 中转（2026-08-07 切换默认，Bearer mk- key）；官方站可设 MINIMAX_API_BASE=https://api.minimaxi.com
CREATE_PATH = "/v2/video_generation"
QUERY_PATH = "/v2/query/video_generation"  # GET 单查 {id} / GET 列表
DELETE_PATH = "/v2/video_generation"       # DELETE {id}

DEFAULT_MODEL = "MiniMax-H3"
DEFAULT_RESOLUTION = "768P"

# 段级时长硬限制（MiniMax 官方：整数 4~15）
DURATION_MIN = 4
DURATION_MAX = 15

# YAML defaults.resolution 兼容映射：seedance 写 720p，MiniMax 为 768P/2K
_RESOLUTION_ALIASES = {
    "720p": "768P",
    "720P": "768P",
    "768p": "768P",
    "2k": "2K",
}


# ---------------------------------------------------------------------------
# 基础 HTTP / 鉴权
# ---------------------------------------------------------------------------


def api_key() -> str:
    return (os.environ.get("MINIMAX_API_KEY") or "").strip()


def default_model() -> str:
    return (os.environ.get("MINIMAX_MODEL") or DEFAULT_MODEL).strip()


def _error_text(payload: dict, default: str) -> str:
    err = payload.get("error") or {}
    msg = err.get("message") or payload.get("message") or default
    rid = payload.get("request_id") or ""
    return f"{msg} (request_id={rid})" if rid else msg


def http_request(
    method: str,
    path: str,
    *,
    body: dict | None = None,
    query: dict[str, str] | None = None,
    timeout: int = 180,
) -> dict[str, Any]:
    """MiniMax REST 封装：Bearer 鉴权 + 非 2xx 抛错（含内部错误码）。"""
    key = api_key()
    if not key:
        raise RuntimeError("未设置 MINIMAX_API_KEY")
    headers = {"Authorization": f"Bearer {key}"}
    url = BASE_URL + path
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            params=query,
            json=body if body is not None else None,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"HTTP 请求失败: {e}") from e
    try:
        payload = resp.json()
    except ValueError:
        payload = {"message": resp.text[:300]}
    if resp.status_code >= 400 or payload.get("type") == "error":
        raise RuntimeError(
            f"{method} {path} -> HTTP {resp.status_code}: "
            f"{_error_text(payload, '未知错误')}"
        )
    return payload


def _task_from_payload(payload: dict) -> dict:
    """统一取 task 对象（query/list 响应结构均为 {task: ...} / {items: [...]}）。"""
    task = payload.get("task")
    if isinstance(task, dict):
        return task
    return payload


# ---------------------------------------------------------------------------
# 指纹 / 对账（本地为主；远程仅 task_id 级，见模块 docstring）
# ---------------------------------------------------------------------------


def _normalize_resolution(res: str | None) -> str:
    r = (res or "").strip() or DEFAULT_RESOLUTION
    return _RESOLUTION_ALIASES.get(r, r)


def _clamp_duration(sec: Any) -> int:
    try:
        v = int(sec)
    except (TypeError, ValueError):
        v = 5
    return max(DURATION_MIN, min(DURATION_MAX, v))


def _clear_submitting(project_root: Path, ep_id: str, sid: str) -> None:
    """删除某 segment 的 submitting 卡位（确认 HTTP 错误未建单后调用，防重复拦截）。"""
    try:
        for t in dedup.find_local_by_identity(
            project_root, kind=KIND_MINIMAX, episode_id=ep_id, identity_key=sid
        ):
            if (t.get("status") or "").strip() == "submitting":
                path = archive_file(project_root, KIND_MINIMAX, ep_id)
                doc = load_doc(path)
                doc["tasks"] = [
                    x for x in doc.get("tasks", []) or []
                    if not (str(x.get("task_id")) == str(t.get("task_id")) and (x.get("status") or "").strip() == "submitting")
                ]
                save_doc(path, doc, kind=KIND_MINIMAX, episode_id=ep_id)
    except Exception:
        pass


def _http_status_of(err: str) -> int | None:
    """从错误文本提取 HTTP 状态码（"-> HTTP 429: ..."）。非 HTTP 错误返回 None。"""
    import re as _re
    m = _re.search(r"-> HTTP (\d{3})", str(err))
    return int(m.group(1)) if m else None


MAX_RATE_LIMIT_RETRY = 6      # 429/503 等待配额释放重试上限
RATE_LIMIT_WAIT_SEC = 45      # 429/503 重试等待（metaso 并发上限约 5，逐段提交时通常 1 轮即可恢复）


def _segment_fingerprint(seg: dict, episode: dict) -> str:
    """segment/shot 内容指纹（model/duration/ratio/resolution 与 build 保持一致）。"""
    try:
        defaults = episode.get("defaults") or {}
        duration = seg.get("duration_sec", defaults.get("duration", 5))
        return dedup.fingerprint_video(
            prompt=dedup.video_text_from_segment(seg),
            model=default_model(),
            duration=_clamp_duration(duration),
            ratio=defaults.get("ratio", "9:16"),
            resolution=_normalize_resolution(defaults.get("resolution", "720p")),
            media_urls=dedup.video_media_urls_from_segment(seg),
        )
    except Exception:
        # 解析失败不应阻塞提交；返回空让对账退化为本地 identity 去重
        return ""


def _status_label(
    sid: str,
    fp: str,
    project_root: Path,
    ep_id: str,
) -> str:
    """✅submitted / ⏳submitting / ❓not_submitted 状态标签（本地指纹判定）。"""
    local = dedup.local_lookup(
        project_root, kind=KIND_MINIMAX, episode_id=ep_id,
        identity_key=sid, fingerprint=fp,
    )
    if local.get("matched") and local.get("kind") == "submitted":
        return f"✅submitted(task_id={local['existing_task'].get('task_id')})"
    if local.get("matched") and local.get("kind") == "submitting":
        return f"⏳submitting({'stale' if local.get('stale') else 'in_progress'})"
    return "❓not_submitted"


def _write_back_remote(
    project_root: Path,
    *,
    episode_id: str,
    remote_task_id: str,
    fingerprint: str,
    identity_key: str,
    extra_params: dict | None = None,
) -> None:
    """远程 task_id 级回写（MiniMax 不回传输入内容，无法按指纹匹配具体 segment）。"""
    # 删同身份 submitting 占位，避免下次对账先撞 submitting 拦下
    for t in dedup.find_local_by_identity(
        project_root, kind=KIND_MINIMAX, episode_id=episode_id, identity_key=identity_key
    ):
        if (t.get("status") or "").strip() == "submitting":
            path = archive_file(project_root, KIND_MINIMAX, episode_id)
            doc = load_doc(path)
            doc["tasks"] = [
                x for x in doc.get("tasks", []) or []
                if str(x.get("task_id")) != str(t.get("task_id"))
            ]
            save_doc(path, doc, kind=KIND_MINIMAX, episode_id=episode_id)
    params: dict[str, Any] = {
        "fingerprint": fingerprint,
        "reconciled_from_remote": True,
        "segment_id": identity_key,
    }
    if extra_params:
        params.update(extra_params)
    add_task(
        kind=KIND_MINIMAX,
        task_id=remote_task_id,
        params=params,
        project_root=project_root,
        status="submitted",
        episode_id=episode_id,
    )


# ---------------------------------------------------------------------------
# 任务生命周期
# ---------------------------------------------------------------------------


def get_task(task_id: str) -> dict[str, Any]:
    path = f"{QUERY_PATH}/{task_id.strip()}"
    payload = http_request("GET", path, timeout=60)
    task = _task_from_payload(payload)
    status = task.get("status") or "unknown"
    content = task.get("content") or {}
    video_url = content.get("url") if isinstance(content, dict) else None
    return {
        "task_id": task_id,
        "status": status,
        "video_url": video_url,
        "task": task,
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
            "page_size": str(min(page_size, 100)),
        }
        if status:
            q["filter.status"] = status
        if model:
            q["filter.model"] = model
        payload = http_request("GET", QUERY_PATH, query=q, timeout=60)
        batch = payload.get("items") or []
        if not batch:
            break
        out.extend(batch)
        if len(batch) < min(page_size, 100):
            break
    return out


def wait_task(
    task_id: str,
    max_wait: int = 600,
    poll_interval: float = 10.0,
) -> dict[str, Any]:
    """轮询直到终态（MiniMax 官方推荐间隔 10s）。"""
    deadline = time.time() + max_wait
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = get_task(task_id)
        st = last.get("status") or ""
        if st in ("succeeded", "failed", "cancelled"):
            _record_status(task_id, st, video_url=last.get("video_url"))
            return last
        time.sleep(poll_interval)
    last["error"] = f"等待超时（{max_wait}s）"
    return last


def _record_status(
    task_id: str,
    status: str,
    *,
    video_url: str | None = None,
    local_mp4: str | None = None,
    project_root: Path | None = None,
    episode: str | None = None,
) -> None:
    """把远程状态回写本地归档（尽力而为，失败不阻塞）。"""
    if not project_root:
        return
    try:
        updates: dict[str, Any] = {"status": status}
        if video_url:
            updates["video_url"] = video_url
        if local_mp4:
            updates["local_mp4"] = local_mp4
        update_task(
            task_id,
            updates,
            project_root=project_root,
            kind=KIND_MINIMAX,
            episode_id=episode or "",
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 提交（create / shots / segments 共用）
# ---------------------------------------------------------------------------


def create_task(
    body: dict[str, Any],
    dry_run: bool = False,
    archive_meta: dict | None = None,
) -> dict[str, Any]:
    archive_meta = archive_meta or {}  # 不带 --project-root 的裸提交也允许（无归档/去重）
    if dry_run:
        return {
            "status": "dry_run",
            "endpoint": BASE_URL + CREATE_PATH,
            "body": sanitize_body_for_log(body),
        }
    # 先算内容指纹写 submitting 卡位（POST 之前落盘）——网络抖动时 MiniMax 可能已建单，
    # 本地却没拿到 response；下次对账会看到卡位，不再盲重发（MiniMax 无内容级远程对账）。
    client_request_id = f"local-{uuid.uuid4()}"
    fingerprint = str(archive_meta.get("fingerprint") or "") if archive_meta else ""
    placeholder_id = client_request_id
    identity_key = archive_meta.get("segment_id") or archive_meta.get("shot_id") or ""
    if archive_meta:
        proot = archive_meta.get("project_root")
        if proot and identity_key:
            try:
                dedup.add_submitting_placeholder(
                    proot,
                    kind=KIND_MINIMAX,
                    episode_id=archive_meta.get("episode"),
                    client_request_id=client_request_id,
                    fingerprint=fingerprint,
                    identity_key=identity_key,
                    extra_params={
                        "segment_id": archive_meta.get("segment_id"),
                        "shot_id": archive_meta.get("shot_id"),
                        "project": archive_meta.get("project") or "",
                    },
                )
            except Exception as e:
                # 归档写失败：API 可能仍会建单，绝不让 agent 闷头重发
                print(
                    f"⚠️ 归档写卡位失败但即将继续 POST，MiniMax 可能已扣费：{e}",
                    file=sys.stderr,
                )
    payload = http_request("POST", CREATE_PATH, body=body, timeout=180)
    tid = str(payload.get("task_id") or "")
    if tid and archive_meta:
        proot = archive_meta.get("project_root")
        if proot:
            try:
                dedup.promote_submitting(
                    proot,
                    kind=KIND_MINIMAX,
                    episode_id=archive_meta.get("episode"),
                    client_request_id=placeholder_id,
                    real_task_id=tid,
                    extra_updates={
                        "fingerprint": fingerprint,
                        "segment_id": archive_meta.get("segment_id"),
                        "shot_id": archive_meta.get("shot_id"),
                        "project": archive_meta.get("project") or "",
                        "episode": str(archive_meta.get("episode") or "").upper(),
                    },
                )
            except Exception:
                # 兜底：保证至少有 submitted 条目
                try:
                    add_task(
                        kind=KIND_MINIMAX,
                        task_id=tid,
                        params={
                            "fingerprint": fingerprint,
                            "segment_id": archive_meta.get("segment_id"),
                            "shot_id": archive_meta.get("shot_id"),
                            "project": archive_meta.get("project") or "",
                            "episode": str(archive_meta.get("episode") or "").upper(),
                        },
                        project_root=proot,
                        status="submitted",
                        episode_id=archive_meta.get("episode"),
                    )
                except Exception:
                    pass
    return {
        "status": "submitted",
        "task_id": tid,
        "response": payload,
    }


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


def build_content_from_simple(
    text: str,
    image_urls: list[tuple[str, str]] | None = None,
    project_root: Path | None = None,
) -> list[dict[str, Any]]:
    """image_urls: [(path_or_url, role), ...] 本地路径自动转 data URI"""
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


# --- shots.yaml 提交 ---


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("需要 PyYAML: pip3 install pyyaml")
        doc = yaml.safe_load(text)
    else:
        doc = json.loads(text)
    if not isinstance(doc, dict):
        raise RuntimeError("yaml 文件根节点须为对象")
    return doc


def _resolve_episode_file(project_root: Path, ep_id: str, kind: str) -> Path | None:
    """定位 EP##_segments.yaml / EP##_shots.yaml，兼容新旧目录布局。

    候选顺序：分集剧本/{ep}_{kind}.yaml > 剧本/{ep}/{ep}_{kind}.yaml
    （仓库现存项目全部使用 剧本/EP##/ 布局，旧脚本默认路径 分集剧本/ 保留兼容）。"""
    for d in (project_root / "分集剧本", project_root / "剧本" / ep_id):
        for suffix in ("yaml", "yml", "json"):
            p = d / f"{ep_id}_{kind}.{suffix}"
            if p.is_file():
                return p
    return None


def role_file_to_path(shot: dict, file_key: str) -> str | None:
    assets = shot.get("assets") or {}
    if file_key == "first_frame":
        return assets.get("first_frame")
    if file_key == "last_frame":
        return assets.get("last_frame")
    for mapping in (assets.get("look_urls") or {}, assets.get("scene_urls") or {},
                    assets.get("prop_urls") or {}):
        if file_key in mapping:
            return mapping[file_key]
    return None


def build_content_array(shot: dict, project_root: Path, cdn_registry: dict | None = None,
                        prompt_suffix: str | None = None,
                        prompt_suffix_silent: str | None = None) -> list[dict]:
    api = shot.get("api") or {}
    # 结构化 api 块（subjects/shots）→ 按 H3 Ref2VA 六段式渲染；无结构化块回退 api.text
    try:
        from prompt_renderer import render as _render_prompt
        text = _render_prompt("minimax", api, prompt_suffix=prompt_suffix,
                              prompt_suffix_silent=prompt_suffix_silent)
    except Exception as e:
        # 渲染器异常不应静默：回退 api.text 但报警，避免掩盖渲染 bug
        print(f"⚠️ prompt_renderer 渲染失败，回退 api.text：{e}", file=sys.stderr)
        text = api.get("text", "")
    content: list[dict] = [{"type": "text", "text": text}]
    for role_spec in api.get("content_roles") or []:
        file_key = role_spec["file"]
        # TOS URL 优先；无注册表/未命中时回退 assets 内 URL 或本地 data URI
        tos_url = lookup_tos_url(file_key, cdn_registry) if cdn_registry else None
        if tos_url:
            url = tos_url
        else:
            rel = role_file_to_path(shot, file_key)
            if not rel:
                raise ValueError(f"{shot.get('shot_id') or shot.get('segment_id')}: 找不到素材 {file_key}")
            url = resolve_image_url(rel, project_root)
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": url},
                "role": role_spec["role"],
            }
        )
    return content


def _build_body(episode: dict, item: dict, project_root: Path, cdn_registry: dict | None) -> dict[str, Any]:
    """segment 与 shot 同构（均含 duration_sec / assets / api.content_roles）。"""
    defaults = episode.get("defaults") or {}
    raw_dur = item.get("duration_sec", defaults.get("duration", 5))
    body: dict[str, Any] = {
        "model": default_model(),
        "content": build_content_array(item, project_root, cdn_registry,
                                        prompt_suffix=defaults.get("prompt_suffix"),
                                        prompt_suffix_silent=defaults.get("prompt_suffix_silent")),
        "ratio": defaults.get("ratio", "9:16"),
        "resolution": _normalize_resolution(defaults.get("resolution", "720p")),
        "duration": _clamp_duration(raw_dur),
    }
    if defaults.get("watermark"):
        body["aigc_watermark"] = True
    return body


def validate_assets(item: dict, project_root: Path) -> list[str]:
    """本地路径缺失检查（http/data 跳过）。"""
    missing = []
    assets = item.get("assets") or {}
    for mapping in (assets.get("look_urls") or {}, assets.get("scene_urls") or {},
                    assets.get("prop_urls") or {}):
        for rel in mapping.values():
            if rel.startswith(("http://", "https://", "data:")):
                continue
            p = project_root / rel if not Path(rel).is_absolute() else Path(rel)
            if not p.is_file():
                missing.append(str(rel))
    # first_frame/last_frame 可能被 content_roles 引用，缺失时 check-only 也应报出
    for key in ("first_frame", "last_frame"):
        rel = assets.get(key)
        if not rel or rel.startswith(("http://", "https://", "data:")):
            continue
        p = project_root / rel if not Path(rel).is_absolute() else Path(rel)
        if not p.is_file():
            missing.append(str(rel))
    return missing


# ---------------------------------------------------------------------------
# 子命令
# ---------------------------------------------------------------------------


def cmd_docs(_: argparse.Namespace) -> int:
    doc = {
        "docs": [
            "https://platform.minimaxi.com/docs/guides/video-generation",
            "https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create",
        ],
        "create": BASE_URL + CREATE_PATH,
        "get": BASE_URL + QUERY_PATH + "/{task_id}",
        "list": BASE_URL + QUERY_PATH,
        "model_default": default_model(),
        "resolution_default": DEFAULT_RESOLUTION,
        "duration_range": [DURATION_MIN, DURATION_MAX],
        "env": ["MINIMAX_API_KEY", "MINIMAX_MODEL"],
        "note": (
            "MiniMax list/query 不回传输入 prompt/参考图，远程对账仅 task_id 级；"
            "防重复扣费以本地指纹为主。任务记录 7 天窗口，成片 URL 限时，提交后及时下载。"
        ),
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
            "model": default_model(),
            "content": build_content_from_simple(args.text, images or None, project_root),
            "ratio": args.ratio or "9:16",
            "resolution": _normalize_resolution(args.resolution or DEFAULT_RESOLUTION),
            "duration": _clamp_duration(args.duration or 5),
        }
        if args.watermark:
            body["aigc_watermark"] = True
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
    # 先查本地归档状态，提前打 cancel 语义提示（MiniMax 仅 queued 可取消，running 不可）
    project_root = None
    if getattr(args, "project_root", None):
        try:
            project_root = assert_valid_drama_project_root(args.project_root)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
    local_status = None
    try:
        for t in _load_all_local_tasks(project_root) if project_root else []:
            if str(t.get("task_id", "")) == str(args.task_id):
                local_status = (t.get("status") or "").lower()
                break
    except Exception:
        local_status = None
    pending_locals = ("pending", "running", "queued", "in_progress", "submitting")
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
    if st in ("queued", "running"):
        print(
            "⚠️ MiniMax 仅 queued 任务可取消（DELETE），running 不可取消；"
            "任务按秒计费至完成。如担心重复扣费，先用 --status / reconcile 核对。",
            file=sys.stderr,
        )
    if project_root:
        _record_status(
            args.task_id, st,
            video_url=info.get("video_url"),
            project_root=project_root,
        )
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_archive_list(args: argparse.Namespace) -> int:
    project_root = assert_valid_drama_project_root(getattr(args, "project_root", None)) \
        if getattr(args, "project_root", None) else None
    tasks = _load_all_local_tasks(project_root) if project_root else []
    print(json.dumps({"tasks": tasks[: getattr(args, "limit", 20)]}, ensure_ascii=False, indent=2))
    return 0


def _load_all_local_tasks(project_root: Path) -> list[dict]:
    """读取 minimax 本地归档（assets/tasks_minimax_video.json，按 kind 隔离）。

    不扫 assets/generated/*/tasks.json——那是 seedance 的归档，混读会误导
    list --local 与 get 的状态提示。"""
    path = archive_file(project_root, KIND_MINIMAX, None)
    if not path.is_file():
        return []
    try:
        return (load_doc(path).get("tasks", []) or [])[:]
    except Exception:
        return []


def cmd_list(args: argparse.Namespace) -> int:
    if args.local:
        return cmd_archive_list(args)
    if not api_key():
        print(json.dumps({"error": "未设置 MINIMAX_API_KEY"}, ensure_ascii=False))
        return 1
    tasks = list_tasks(args.status, args.model, args.page_size, args.max_pages)
    if args.json:
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
        return 0
    for t in tasks:
        tid = str(t.get("id") or t.get("task_id") or "")
        st = str(t.get("status") or "?")
        content = t.get("content") or {}
        vu = content.get("url") if isinstance(content, dict) else None
        preview = (vu[:72] + "…") if vu and len(vu) > 72 else (vu or "")
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
    if not url:
        print(json.dumps({"error": "无 video_url，请确认任务已成功"}, ensure_ascii=False))
        return 1
    out = args.output or safe_mp4_name(args.task_id or "minimax")
    try:
        resp = requests.get(url, timeout=600, stream=True)
        resp.raise_for_status()
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(json.dumps({"error": f"下载失败: {e}"}, ensure_ascii=False))
        return 1
    # 回写本地归档 local_mp4 + succeeded（尽力而为）
    project_root = None
    if getattr(args, "project_root", None):
        try:
            project_root = assert_valid_drama_project_root(args.project_root)
        except ValueError:
            project_root = None
    if project_root and args.task_id:
        _record_status(
            args.task_id, "succeeded",
            video_url=url,
            local_mp4=str(Path(out).resolve()),
            project_root=project_root,
        )
    print(json.dumps({"status": "ok", "output": str(Path(out).resolve()), "size": Path(out).stat().st_size},
                     ensure_ascii=False, indent=2))
    return 0


def safe_mp4_name(seed: str) -> str:
    safe = "".join(c for c in seed if c.isalnum() or c in "-_") or "minimax"
    return f"{safe}.mp4"


def _coordination_block(
    *,
    project_root: Path,
    ep_id: str,
    args: argparse.Namespace,
) -> dict[str, dict] | None:
    """segments 与 shots 共用的对账前置。

    MiniMax list 不回传输入 prompt/参考图 → 无法内容级远程匹配，恒返回 None
    （本地指纹是主防线）。保留参数兼容 seedance CLI 行为。
    """
    ok_force, force_msg = dedup.require_force_confirm(args.force)
    if args.force and not ok_force:
        print(force_msg, file=sys.stderr)
        args.force = False
    return None


def _precheck_duplicates(project_root: Path, ep_id: str) -> list[str]:
    """提交前强制本地预检：同段多个 submitted = 重复扣费风险；stale submitting（>1h 未结算）。返回问题列表。"""
    problems: list[str] = []
    try:
        doc = load_doc(archive_file(project_root, KIND_MINIMAX, ep_id))
        tasks = doc.get("tasks", []) or []
    except Exception:
        return problems
    seg_submitted: dict[str, list] = {}
    now = time.time()
    for t in tasks:
        seg = (t.get("params") or {}).get("segment_id") or ""
        st = (t.get("status") or "").strip()
        if st == "submitted" and seg and seg != "(reconciled)":  # reconcile 杂项段不计入段级重复检测
            seg_submitted.setdefault(seg, []).append(str(t.get("task_id")))
        if st == "submitting":
            ts = t.get("updated_at") or t.get("created_at") or 0
            age = 0.0
            try:
                age = time.time() - float(ts)  # 数字时间戳
            except (TypeError, ValueError):
                try:  # ISO 字符串（如 2026-08-07T18:13:07.369851）
                    from datetime import datetime as _dt
                    age = time.time() - _dt.fromisoformat(str(ts)).timestamp()
                except Exception:
                    age = 0.0
            if age > 3600:
                problems.append(f"stale submitting: {seg} {t.get('task_id')}（>1h 未结算，先 reconcile 核实远程状态）")
    for seg, tids in seg_submitted.items():
        if len(tids) > 1:
            problems.append(f"重复提交风险: {seg} 已有 {len(tids)} 个 submitted 任务 {tids}（先 reconcile + 人工确认再继续）")
    return problems


def _run_submit_loop(
    *,
    episode: dict,
    items: list[dict],
    id_field: str,
    project_root: Path,
    ep_id: str,
    args: argparse.Namespace,
    cdn_registry: dict | None = None,
) -> tuple[list[dict[str, Any]], int, int]:
    """segments / shots 共用提交循环（对账 → 校验 → dry-run/提交）。"""
    # 提交前强制预检（硬约束）：重复提交/卡位异常 → 阻止提交，除非 --force + ARK_ALLOW_FORCE=1 显式覆盖
    problems = _precheck_duplicates(project_root, ep_id)
    if problems and not (args.force and os.environ.get("ARK_ALLOW_FORCE") == "1"):
        print("⛔ 提交前预检发现异常，已阻止（确认后可 --force + ARK_ALLOW_FORCE=1 覆盖）：", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return [{"error": "precheck_blocked", "problems": problems}], 0, 0
    if problems:
        print("⚠️ 预检警告（--force 覆盖，请确认已人工核实）：", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
    results: list[dict[str, Any]] = []
    ready = skipped = 0

    for item in items:
        sid = str(item.get(id_field) or "?")
        fp = _segment_fingerprint(item, episode)
        # --- 对账（本地指纹为主）；--force 仅绕过 submitting 卡位，已 submitted 始终跳过（防重复扣费）---
        local = dedup.local_lookup(
            project_root, kind=KIND_MINIMAX, episode_id=ep_id,
            identity_key=sid, fingerprint=fp,
        )
        if local.get("matched") and local.get("kind") == "submitted":
            et = local["existing_task"].get("task_id")
            results.append({id_field: sid, "status": "already_submitted", "existing_task_id": et})
            print(f"⊙ {sid} 本地命中已提交 (task_id={et})，skip", file=sys.stderr)
            continue
        if local.get("matched") and local.get("kind") == "submitting" and not args.force:
            results.append({id_field: sid, "status": "submitting_blocked",
                            "reason": "本地 submitting 卡位未结算（MiniMax 无内容级远程对账，不盲重发）"})
            print(
                f"⛔ {sid} 本地 submitting 卡位未结算（可能 MiniMax 已扣费）。"
                f"如确认原请求未真发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
                file=sys.stderr,
            )
            continue
        if item.get("mode") == "skip":
            skipped += 1
            continue
        miss = validate_assets(item, project_root)
        if miss:
            results.append({id_field: sid, "status": "missing_assets", "missing": miss})
            if args.check_only:
                print(f"✗ {sid} 缺 {len(miss)} 个文件", file=sys.stderr)
            continue
        ready += 1
        if args.check_only:
            print(f"✓ {sid} 素材齐全", file=sys.stderr)
            continue
        try:
            body = _build_body(episode, item, project_root, cdn_registry)
            if args.dry_run:
                results.append({id_field: sid, "status": "dry_run", "body": sanitize_body_for_log(body)})
                continue
            # 429/503 配额限制自动重试；402 积分不足停止整批；明确 HTTP 错误清卡位防下次拦截
            attempt = 0
            while True:
                try:
                    r = create_task(
                        body,
                        dry_run=False,
                        archive_meta={
                            id_field: sid,
                            "episode": ep_id,
                            "project_root": str(project_root),
                            "project": project_root.name,
                            "fingerprint": fp,
                        },
                    )
                    r[id_field] = sid
                    results.append(r)
                    time.sleep(args.delay)
                    break
                except Exception as e:
                    code = _http_status_of(str(e))
                    if code == 402:
                        _clear_submitting(project_root, ep_id, sid)  # 未建单，清卡位
                        results.append({id_field: sid, "status": "quota_exhausted", "error": str(e)})
                        break
                    if code in (429, 503) and attempt < MAX_RATE_LIMIT_RETRY:
                        attempt += 1
                        print(
                            f"⏳ {sid} 配额限制(HTTP {code})，等待 {RATE_LIMIT_WAIT_SEC}s 重试 ({attempt}/{MAX_RATE_LIMIT_RETRY})",
                            file=sys.stderr,
                        )
                        time.sleep(RATE_LIMIT_WAIT_SEC)
                        continue
                    if code is not None:
                        _clear_submitting(project_root, ep_id, sid)  # 明确 4xx/5xx = 未建单
                    results.append({id_field: sid, "status": "error", "error": str(e)})
                    break
        except Exception as e:
            results.append({id_field: sid, "status": "error", "error": str(e)})
    # 提交后自动对账摘要（每轮必看：0 重复/0 孤儿才继续下一轮）
    from collections import Counter as _Counter
    _c = _Counter(r.get("status") for r in results)
    print(f"提交汇总: {dict(_c)}", file=sys.stderr)
    if _c.get("quota_exhausted"):
        print("⚠️ H3 积分余额不足——请充值后重跑（已自动停止，勿用 --force 整批重发）", file=sys.stderr)
    return results, ready, skipped


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
        else _resolve_episode_file(project_root, ep_id, "segments")
    )
    if not seg_path:
        print(json.dumps({"error": f"找不到 {ep_id}_segments.yaml（分集剧本/ 或 剧本/{ep_id}/）"}, ensure_ascii=False))
        return 1

    episode = load_yaml_or_json(seg_path)
    segments = episode.get("segments") or []
    if args.segment:
        segments = [s for s in segments if s.get("segment_id") == args.segment]
        if not segments:
            print(json.dumps({"error": f"未找到 {args.segment}"}, ensure_ascii=False))
            return 1

    _coordination_block(project_root=project_root, ep_id=ep_id, args=args)

    # CDN registry（TOS URL 兜底：YAML assets 已是 https 时无需）
    cdn_registry: dict | None = None
    registry_config = episode.get("image_cdn_registry")
    if registry_config and isinstance(registry_config, dict):
        cdn_registry = load_cdn_registry(registry_config, project_root)

    # --status：只打印每段状态，绝不提交
    if getattr(args, "status", False):
        results = []
        for seg in segments:
            sid = seg.get("segment_id", "?")
            st = _status_label(sid, _segment_fingerprint(seg, episode), project_root, ep_id)
            print(st, file=sys.stderr)
            results.append({"segment_id": sid, "status": st})
        print(json.dumps({"episode": ep_id, "results": results}, ensure_ascii=False, indent=2))
        return 0

    results, ready, _skipped = _run_submit_loop(
        episode=episode, items=segments, id_field="segment_id",
        project_root=project_root, ep_id=ep_id, args=args,
        cdn_registry=cdn_registry,
    )
    summary = {
        "episode": ep_id,
        "ready": ready,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.check_only and any(r.get("status") == "missing_assets" for r in results):
        return 1
    if any(r.get("status") == "error" for r in results):
        return 1
    return 0


def cmd_shots(args: argparse.Namespace) -> int:
    try:
        project_root = assert_valid_drama_project_root(args.project_root)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    ep_id = args.episode.upper()
    shots_path = (
        Path(args.shots_file).expanduser().resolve()
        if args.shots_file
        else _resolve_episode_file(project_root, ep_id, "shots")
    )
    if not shots_path:
        print(json.dumps({"error": f"找不到 {ep_id}_shots.yaml（分集剧本/ 或 剧本/{ep_id}/）"}, ensure_ascii=False))
        return 1

    episode = load_yaml_or_json(shots_path)
    shots = episode.get("shots") or []
    if args.shot:
        shots = [s for s in shots if s.get("shot_id") == args.shot]
        if not shots:
            print(json.dumps({"error": f"未找到 {args.shot}"}, ensure_ascii=False))
            return 1

    _coordination_block(project_root=project_root, ep_id=ep_id, args=args)

    # CDN registry（TOS URL 兜底：YAML assets 已是 https 时无需）
    cdn_registry: dict | None = None
    registry_config = episode.get("image_cdn_registry")
    if registry_config and isinstance(registry_config, dict):
        cdn_registry = load_cdn_registry(registry_config, project_root)

    # --status：只打印每个 shot 状态，绝不提交
    if getattr(args, "status", False):
        results = []
        for shot in shots:
            sid = shot.get("shot_id", "?")
            st = _status_label(sid, _segment_fingerprint(shot, episode), project_root, ep_id)
            print(st, file=sys.stderr)
            results.append({"shot_id": sid, "status": st})
        print(json.dumps({"episode": ep_id, "results": results}, ensure_ascii=False, indent=2))
        return 0

    results, ready, skipped = _run_submit_loop(
        episode=episode, items=shots, id_field="shot_id",
        project_root=project_root, ep_id=ep_id, args=args,
        cdn_registry=cdn_registry,
    )
    summary = {
        "episode": ep_id,
        "skipped": skipped,
        "ready": ready,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.check_only and any(r.get("status") == "missing_assets" for r in results):
        return 1
    if any(r.get("status") == "error" for r in results):
        return 1
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    """拉 7 天远程任务，把远程存在但本地缺的归档回写（task_id 级，无法内容匹配）。

    MiniMax list 不回传输入 prompt/参考图 → 无法按指纹匹配具体 segment；
    本命令保证「远程已建单的不再被盲重发」，具体 segment 是否已提交以本地归档为准。"""
    try:
        project_root = assert_valid_drama_project_root(args.project_root)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    ep_id = args.episode.upper()

    try:
        remote_tasks = list_tasks(model=default_model(), page_size=100, max_pages=6)
    except Exception as e:
        print(json.dumps({"error": f"远程任务拉取失败：{e}"}, ensure_ascii=False))
        return 1

    results: list[dict[str, Any]] = []
    idx = dedup.read_local_index(project_root, kind=KIND_MINIMAX, episode_id=ep_id)
    existing_ids = {str(t.get("task_id") or "") for t in idx.values()}
    written = 0
    for rt in remote_tasks:
        rtid = str(rt.get("id") or rt.get("task_id") or "")
        if not rtid or rtid in existing_ids:
            continue
        try:
            _write_back_remote(
                project_root, episode_id=ep_id, remote_task_id=rtid,
                fingerprint="", identity_key="(reconciled)",
                extra_params={"project": project_root.name,
                              "remote_status": str(rt.get("status") or "")},
            )
            written += 1
            results.append({"status": "reconciled_from_remote", "task_id": rtid,
                            "remote_status": rt.get("status")})
        except Exception as e:
            results.append({"status": "write_back_failed", "task_id": rtid, "error": str(e)})

    print(json.dumps({
        "episode": ep_id,
        "remote_count": len(remote_tasks),
        "written": written,
        "note": "MiniMax 不回传输入内容，仅 task_id 级回写；segment 级状态请用 --status",
        "results": results,
    }, ensure_ascii=False, indent=2))
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="MiniMax-H3 视频生成 CLI（V2 多模态）")
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
    p_create.add_argument("--ratio", default="9:16")
    p_create.add_argument("--resolution", default=DEFAULT_RESOLUTION)
    p_create.add_argument("--duration", type=int, default=5)
    p_create.add_argument("--watermark", action="store_true", help="添加 AIGC 水印")
    p_create.add_argument("--dry-run", action="store_true")
    p_create.add_argument("--project-root", help="本地图片路径相对根目录")
    p_create.add_argument("--episode", default="", help="集数标记，如 EP01")
    p_create.set_defaults(func=cmd_create)

    p_get = sub.add_parser("get")
    p_get.add_argument("--task-id", required=True)
    p_get.add_argument("--project-root", help="短剧项目根，用于回写本地归档")
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status")
    p_list.add_argument("--model")
    p_list.add_argument("--page-size", type=int, default=50)
    p_list.add_argument("--max-pages", type=int, default=5)
    p_list.add_argument("--json", action="store_true")
    p_list.add_argument("--local", action="store_true", help="读本地归档而非远程 API")
    p_list.add_argument("--project-root", help="--local 时指定短剧项目根")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_wait = sub.add_parser("wait")
    p_wait.add_argument("--task-id", required=True)
    p_wait.add_argument("--max-wait", type=int, default=600)
    p_wait.add_argument("--interval", type=float, default=10.0)
    p_wait.set_defaults(func=cmd_wait)

    p_dl = sub.add_parser("download")
    p_dl.add_argument("--task-id")
    p_dl.add_argument("--url")
    p_dl.add_argument("--output", "-o")
    p_dl.add_argument("--project-root", help="短剧项目根，用于回写本地归档 local_mp4")
    p_dl.set_defaults(func=cmd_download)

    p_rec = sub.add_parser("reconcile", help="拉近 7 天远程任务回写本地归档（task_id 级）")
    p_rec.add_argument("episode", help="如 EP01")
    p_rec.add_argument("--project-root", required=True, help="短剧项目根，如 dramas/<剧名>")
    p_rec.set_defaults(func=cmd_reconcile)

    p_shots = sub.add_parser("shots", help="从 EP##_shots.yaml 提交")
    p_shots.add_argument("episode", help="如 EP01")
    p_shots.add_argument("--project-root", required=True, help="短剧项目根，如 dramas/<剧名>")
    p_shots.add_argument("--shots-file", help="覆盖默认 分集剧本/EP##_shots.yaml")
    p_shots.add_argument("--shot", help="仅指定 shot_id")
    p_shots.add_argument("--check-only", action="store_true")
    p_shots.add_argument("--dry-run", action="store_true")
    p_shots.add_argument("--delay", type=float, default=0.5)
    p_shots.add_argument("--force", action="store_true", help="忽略去重检查，强制重新提交（需 ARK_ALLOW_FORCE=1）")
    p_shots.add_argument("--check-remote", action="store_true", help="（保留兼容）远程对账仅 task_id 级")
    p_shots.add_argument("--no-remote", action="store_true", help="（保留兼容）MiniMax 无远程内容对账，默认即仅本地去重")
    p_shots.add_argument("--pending", action="store_true", help="（保留兼容）默认已按本地指纹增量跳过，本参数无额外作用")
    p_shots.add_argument("--status", action="store_true", help="只打印每个 shot 状态，不提交")
    p_shots.set_defaults(func=cmd_shots)

    p_seg = sub.add_parser("segments", help="从 EP##_segments.yaml 提交段落视频")
    p_seg.add_argument("episode", help="如 EP01")
    p_seg.add_argument("--project-root", required=True, help="短剧项目根，如 dramas/<剧名>")
    p_seg.add_argument("--segments-file", help="覆盖默认 分集剧本/EP##_segments.yaml")
    p_seg.add_argument("--segment", help="仅指定 segment_id")
    p_seg.add_argument("--check-only", action="store_true")
    p_seg.add_argument("--dry-run", action="store_true")
    p_seg.add_argument("--delay", type=float, default=0.5)
    p_seg.add_argument("--force", action="store_true", help="忽略去重检查，强制重新提交（需 ARK_ALLOW_FORCE=1）")
    p_seg.add_argument("--check-remote", action="store_true", help="（保留兼容）远程对账仅 task_id 级")
    p_seg.add_argument("--no-remote", action="store_true", help="（保留兼容）MiniMax 无远程内容对账，默认即仅本地去重")
    p_seg.add_argument("--pending", action="store_true", help="（保留兼容）默认已按本地指纹增量跳过，本参数无额外作用")
    p_seg.add_argument("--status", action="store_true", help="只打印每段状态，不提交")
    p_seg.set_defaults(func=cmd_segments)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
