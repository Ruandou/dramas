#!/usr/bin/env python3
"""Load ARK/TOS creds from .cursor/mcp.json then run seedream batch / tos sync."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    # Sandbox proxy often 403s Ark; clear when running outside sandbox.
    for k in (
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
        "GIT_HTTP_PROXY", "GIT_HTTPS_PROXY", "SOCKS_PROXY", "SOCKS5_PROXY",
        "socks_proxy", "socks5_proxy",
    ):
        os.environ.pop(k, None)
    for p in (REPO / ".cursor" / "mcp.json", Path.home() / ".cursor" / "mcp.json"):
        if not p.is_file():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for server in ("volc-ark", "volc-jimeng"):
            env = (data.get("mcpServers") or {}).get(server, {}).get("env") or {}
            for k, v in env.items():
                if not v or "REPLACE" in str(v) or "你的" in str(v):
                    continue
                if k == "VOLC_ARK_API_KEY" and not os.environ.get("ARK_API_KEY"):
                    os.environ["ARK_API_KEY"] = str(v).strip()
                elif k not in os.environ or not os.environ.get(k):
                    os.environ[k] = str(v).strip()
    if os.environ.get("VOLC_ARK_API_KEY") and not os.environ.get("ARK_API_KEY"):
        os.environ["ARK_API_KEY"] = os.environ["VOLC_ARK_API_KEY"]


def main() -> int:
    load_env()
    if not os.environ.get("ARK_API_KEY"):
        print("ERROR: ARK_API_KEY missing", file=sys.stderr)
        return 2
    mode = sys.argv[1] if len(sys.argv) > 1 else "props"
    if mode == "props":
        yaml = PROJECT / "assets" / "seedream_batch_props.yaml"
        cmd = [
            sys.executable,
            str(REPO / "mcps/volc-ark/scripts/ark_seedream_image.py"),
            "batch",
            "--yaml",
            str(yaml),
            "--project-root",
            str(PROJECT),
            "--ratio",
            "9:16",
            "--delay",
            "2",
            "--pending",
        ]
        if len(sys.argv) > 2:
            cmd.extend(["--ids", sys.argv[2]])
    elif mode in ("looks", "looks_l02"):
        yaml = PROJECT / "assets" / (
            "seedream_batch_looks_l02.yaml" if mode == "looks_l02" else "seedream_batch_looks.yaml"
        )
        cmd = [
            sys.executable,
            str(REPO / "mcps/volc-ark/scripts/ark_seedream_image.py"),
            "batch",
            "--yaml",
            str(yaml),
            "--project-root",
            str(PROJECT),
            "--ratio",
            "9:16",
            "--delay",
            "2",
            "--pending",
        ]
        if len(sys.argv) > 2:
            cmd.extend(["--ids", sys.argv[2]])
    elif mode == "scenes":
        yaml = PROJECT / "assets" / "seedream_batch_scenes.yaml"
        cmd = [
            sys.executable,
            str(REPO / "mcps/volc-ark/scripts/ark_seedream_image.py"),
            "batch",
            "--yaml",
            str(yaml),
            "--project-root",
            str(PROJECT),
            "--ratio",
            "9:16",
            "--delay",
            "2",
            "--pending",
        ]
        if len(sys.argv) > 2:
            cmd.extend(["--ids", sys.argv[2]])
    elif mode == "tos":
        cmd = [
            sys.executable,
            str(REPO / "mcps/volc-ark/scripts/tos_upload.py"),
            "sync",
            "--project-root",
            str(PROJECT),
        ]
    else:
        print("usage: _run_seedream_batch.py props|looks|looks_l02|scenes|tos [ids]", file=sys.stderr)
        return 2
    print("RUN", " ".join(cmd[:6]), "...", flush=True)
    return subprocess.call(cmd, env=os.environ.copy(), cwd=str(REPO))


if __name__ == "__main__":
    raise SystemExit(main())
