#!/usr/bin/env python3
"""火山方舟 API 公共工具（Bearer ARK_API_KEY）。"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE = "https://ark.cn-beijing.volces.com"
TASKS_PATH = "/api/v3/contents/generations/tasks"
RESPONSES_PATH = "/api/v3/responses"


def api_key() -> str:
    return (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY") or "").strip()


def base_url() -> str:
    return (os.environ.get("ARK_BASE_URL") or DEFAULT_BASE).rstrip("/")


def require_key() -> str:
    key = api_key()
    if not key:
        raise RuntimeError("未设置 ARK_API_KEY 或 VOLC_ARK_API_KEY")
    return key


def http_request(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    query: dict[str, str] | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    key = require_key()
    url = base_url() + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = None
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {detail or e.reason}") from e
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"响应非 JSON: {raw[:500]}") from e


def download_url(url: str, dest_path: str, timeout: int = 300) -> dict[str, Any]:
    from pathlib import Path

    dest = Path(dest_path).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "volc-ark-cli/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return {"path": str(dest.resolve()), "bytes": len(data), "url": url}


def walk_video_url(obj: Any, depth: int = 0) -> str | None:
    if depth > 14:
        return None
    if isinstance(obj, str) and obj.startswith("http"):
        low = obj.lower()
        if ".mp4" in low or "video" in low or "tos-cn" in low:
            return obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "video" in k.lower() and "url" in k.lower() and isinstance(v, str) and v.startswith("http"):
                return v
            hit = walk_video_url(v, depth + 1)
            if hit:
                return hit
    if isinstance(obj, list):
        for x in obj:
            hit = walk_video_url(x, depth + 1)
            if hit:
                return hit
    return None


def extract_video_url(task: dict[str, Any]) -> str | None:
    content = task.get("content")
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = None
    if isinstance(content, dict):
        u = content.get("video_url") or content.get("videoUrl") or content.get("url")
        if isinstance(u, str) and u.startswith("http"):
            return u
    return walk_video_url(task)


def task_id_from_response(resp: dict[str, Any]) -> str | None:
    for key in ("id", "task_id"):
        v = resp.get(key)
        if v:
            return str(v)
    data = resp.get("data")
    if isinstance(data, dict):
        for key in ("id", "task_id"):
            v = data.get(key)
            if v:
                return str(v)
    return None


def task_status(task: dict[str, Any]) -> str:
    return str(task.get("status") or "").lower()


def extract_task_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("tasks", "items", "list", "data", "result"):
        v = payload.get(key)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
        if isinstance(v, dict):
            for sub in ("tasks", "items", "list", "records", "generations", "results"):
                if isinstance(v.get(sub), list):
                    return [x for x in v[sub] if isinstance(x, dict)]
    return []


def safe_mp4_name(name: str) -> str:
    base = name.strip().replace(".mp4", "")
    base = re.sub(r'[/\\:*?"<>|]', "_", base)
    return base + ".mp4" if base else "seedance.mp4"
