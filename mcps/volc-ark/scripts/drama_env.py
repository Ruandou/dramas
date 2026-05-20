"""从 Cursor mcp.json 补全 ARK_API_KEY / DRAMA_PROJECT_ROOT（CLI 与 MCP 共用）。"""
from __future__ import annotations

import json
import os
from pathlib import Path


def _read_mcp_env(repo_root: Path, server: str) -> dict:
    for p in (repo_root / ".cursor" / "mcp.json", Path.home() / ".cursor" / "mcp.json"):
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        env = (data.get("mcpServers") or {}).get(server, {}).get("env") or {}
        if isinstance(env, dict):
            return env
    return {}


def _usable(value: str) -> bool:
    s = (value or "").strip()
    if not s:
        return False
    for bad in ("REPLACE_WITH", "你的", "API Key", "APIKey", "…"):
        if bad in s:
            return False
    return True


def ensure_credentials(repo_root: Path, drama_root: Path | None = None) -> None:
    """未 export 时尝试读取 volc-ark 的 mcp env。"""
    if not (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY")):
        env = _read_mcp_env(repo_root, "volc-ark")
        key = env.get("ARK_API_KEY") or env.get("VOLC_ARK_API_KEY")
        if _usable(str(key or "")):
            os.environ["ARK_API_KEY"] = str(key).strip()

    if drama_root and not os.environ.get("DRAMA_PROJECT_ROOT"):
        env = _read_mcp_env(repo_root, "volc-ark")
        root = env.get("DRAMA_PROJECT_ROOT") or env.get("ARK_PROJECT_ROOT")
        if _usable(str(root or "")):
            os.environ["DRAMA_PROJECT_ROOT"] = str(Path(str(root)).expanduser().resolve())
