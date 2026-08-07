#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHAR-001-L02/L03 generator (Stage 3b-G 2026-08-07).
Reads prompts verbatim from 资产/角色卡片.md; uses official L01 cand2 as --image-url reference.
Run from workspace root:
  python3 dramas/剑宗小祖宗/assets/run_char001_l02l03.py
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/lei/Movies/demo1")
CARD = ROOT / "dramas/剑宗小祖宗/资产/角色卡片.md"
CLI = ROOT / "mcps/gpt-image/scripts/gpt_image.py"
CAND2_URL = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/剑宗小祖宗/CHAR-001-L01-cand2.png"


def prompt_from_card(look_id: str) -> str:
    text = CARD.read_text(encoding="utf-8")
    for ln in text.split("\n"):
        if ln.startswith("| `" + look_id + "` |") and "SAME person" in ln:
            ticks = [j for j, c in enumerate(ln) if c == "`"]
            if len(ticks) >= 4:
                return ln[ticks[2] + 1:ticks[-1]]
    raise SystemExit(f"prompt for {look_id} not found in card")


def load_env():
    with open(ROOT / ".cursor/mcp.json") as f:
        mcp = json.load(f)
    g = mcp["mcpServers"]["gpt-image"]["env"]
    env = dict(os.environ)
    env["GPT_IMAGE_API_KEY"] = g["GPT_IMAGE_API_KEY"]
    env["GPT_IMAGE_BASE_URL"] = g.get("GPT_IMAGE_BASE_URL", "https://api.getgoapi.com")
    env["GPT_IMAGE_MODEL"] = g.get("GPT_IMAGE_MODEL", "gpt-image-2")
    env["GPT_IMAGE_RESPONSE_FORMAT"] = "none"
    env["ARK_ALLOW_FORCE"] = "1"
    return env


def main():
    env = load_env()
    targets = [
        ("CHAR-001-L02", "dramas/剑宗小祖宗/assets/looks/CHAR-001-L02.png"),
        ("CHAR-001-L03", "dramas/剑宗小祖宗/assets/looks/CHAR-001-L03.png"),
    ]
    for look_id, out in targets:
        prompt = prompt_from_card(look_id)
        out_path = ROOT / out
        print(f"=== Generating {look_id} ...", flush=True)
        cmd = [
            sys.executable, str(CLI), "generate",
            "--prompt", prompt,
            "--output", str(out_path),
            "--model", "gpt-image-2",
            "--size", "1600x2848",
            "--force",
            "--image-url", CAND2_URL,
        ]
        r = subprocess.run(cmd, env=env, cwd=ROOT, capture_output=True, text=True, timeout=900)
        if r.stdout:
            print(r.stdout[-6000:], flush=True)
        if r.stderr:
            print("STDERR:", r.stderr[-3000:], flush=True)
        if r.returncode != 0 or not out_path.exists():
            print(f"!!! {look_id} FAILED rc={r.returncode}", flush=True)
        else:
            print(f"OK {look_id} -> {out_path} ({out_path.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
