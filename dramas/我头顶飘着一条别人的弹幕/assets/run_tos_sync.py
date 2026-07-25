#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOS upload wrapper — bootstraps VOLC/TOS creds from .cursor/mcp.json then runs tos_upload sync."""
import os, json, runpy, sys
from pathlib import Path

REPO = Path("/Users/leifu/Movies/dramas")
for p in (REPO / ".cursor" / "mcp.json", Path.home() / ".cursor" / "mcp.json"):
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        servers = data.get("mcpServers") or {}
        for srv in ("volc-ark", "volc-jimeng"):
            env = (servers.get(srv) or {}).get("env") or {}
            for k, v in env.items():
                if v and not os.environ.get(k):
                    os.environ[k] = str(v)

sys.argv = ["tos_upload.py", "sync", "--project-root",
            "dramas/我头顶飘着一条别人的弹幕"]
os.chdir(str(REPO))
runpy.run_path(str(REPO / "mcps" / "volc-ark" / "scripts" / "tos_upload.py"),
               run_name="__main__")
