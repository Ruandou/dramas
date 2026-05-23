#!/usr/bin/env python3
"""本地图片 → API 可用的 URL（公网 HTTPS 或 data URI），无需图床。"""
from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

MIME_BY_SUFFIX = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
}


def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in MIME_BY_SUFFIX:
        return MIME_BY_SUFFIX[ext]
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "image/png"


def file_to_data_uri(path: Path) -> str:
    mime = guess_mime(path)
    raw = path.read_bytes()
    if len(raw) > 30 * 1024 * 1024:
        raise ValueError(f"图片超过 30MB: {path}")
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def file_to_data_uri_generic(path: Path, max_bytes: int = 30 * 1024 * 1024) -> str:
    mime = guess_mime(path)
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"文件超过 {max_bytes // (1024*1024)}MB: {path}")
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def resolve_media_url(
    path_or_url: str,
    project_root: Path | None = None,
) -> str:
    """本地图片或音频 → data URI；http(s)/data: 原样返回。"""
    s = path_or_url.strip()
    if not s:
        raise ValueError("媒体路径为空")
    if s.startswith(("http://", "https://", "data:")):
        return s
    p = Path(s).expanduser()
    if not p.is_absolute() and project_root is not None:
        p = project_root / p
    p = p.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"本地媒体不存在: {p}")
    return file_to_data_uri_generic(p)


def resolve_image_url(
    path_or_url: str,
    project_root: Path | None = None,
) -> str:
    """
    - 已是 http(s) 或 data: → 原样返回
    - 否则视为本地路径（可相对 project_root）→ data URI
    """
    return resolve_media_url(path_or_url, project_root)


# --- TOS CDN registry support ---


def load_cdn_registry(
    registry_config: dict[str, str],
    project_root: Path,
) -> dict[str, dict[str, Any]]:
    """Load cdn_urls.json files and merge into a unified key→entry map.

    registry_config: e.g. {"looks": "assets/looks/cdn_urls.json", "scenes": "assets/scenes/cdn_urls.json"}
    Returns: {"CHAR-001-L01": {"tos_url": "https://...", ...}, "SCENE-001": {...}, ...}
    """
    merged: dict[str, dict[str, Any]] = {}
    for _category, rel_path in registry_config.items():
        p = project_root / rel_path
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for key, entry in data.items():
            if key.startswith("_"):
                continue
            if isinstance(entry, dict):
                merged[key] = entry
    return merged


def lookup_tos_url(
    file_key: str,
    cdn_registry: dict[str, dict[str, Any]] | None,
) -> str | None:
    """Look up a permanent TOS URL for the given asset key.

    Returns the tos_url string if found, else None.
    """
    if not cdn_registry:
        return None
    entry = cdn_registry.get(file_key)
    if not entry:
        return None
    tos = entry.get("tos_url")
    if tos and isinstance(tos, str) and tos.startswith("https://"):
        return tos
    return None
