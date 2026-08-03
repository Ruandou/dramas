#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDN registry（cdn_urls.json）更新工具（Seedream / gpt-image 共用）。"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def update_cdn_urls_json(
    output: Path,
    cdn_url: str,
    task_id: str | None,
    model: str | None,
    size: str | None,
    project_root: Path | None = None,
) -> Path | None:
    """Upsert the CDN URL entry into the appropriate cdn_urls.json.

    Returns the path to the updated cdn_urls.json, or None if skipped.
    """
    out_str = str(output)
    # Determine asset type from output path
    if "/looks/" in out_str:
        asset_type = "looks"
    elif "/scenes/" in out_str:
        asset_type = "scenes"
    else:
        return None  # Not in a known asset directory; skip

    # Determine project root
    root = project_root
    if root is None:
        env_root = os.environ.get("DRAMA_PROJECT_ROOT")
        if env_root:
            root = Path(env_root)
    if root is None:
        # Try to infer from output path: walk up to find assets/ dir
        candidate = output.parent
        for _ in range(10):
            if (candidate / "assets").is_dir():
                root = candidate
                break
            if candidate.parent == candidate:
                break
            candidate = candidate.parent
    if root is None:
        return None

    cdn_json_path = root / "assets" / asset_type / "cdn_urls.json"
    cdn_json_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing
    registry: dict[str, Any] = {}
    if cdn_json_path.is_file():
        try:
            registry = json.loads(cdn_json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            registry = {}

    # Asset ID = filename stem (e.g. CHAR-001-L01.png -> CHAR-001-L01)
    asset_id = output.stem

    now = datetime.now().astimezone()
    expires = now + timedelta(hours=24)

    registry[asset_id] = {
        "local": output.name,
        "cdn_url": cdn_url,
        "task_id": str(task_id) if task_id else None,
        "generated_at": now.isoformat(timespec="seconds"),
        "expires_at": expires.isoformat(timespec="seconds"),
        "model": model,
        "size": size,
    }

    cdn_json_path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return cdn_json_path
