#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHAR-002 / CHAR-003 / CHAR-GRP-12 L01 generator (Stage 3b-G).
Reads GPT_IMAGE_API_KEY from .cursor/mcp.json without printing it.
Run from workspace root: python3 dramas/剑宗小祖宗/assets/run_char002_003_grp12_l01_gen.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts_3b import PROMPTS, META

ROOT = Path("/Users/lei/Movies/demo1")
CLI = ROOT / "mcps/gpt-image/scripts/gpt_image.py"


def main():
    with open(ROOT / ".cursor/mcp.json") as f:
        mcp = json.load(f)
    gpt_env = mcp["mcpServers"]["gpt-image"]["env"]
    api_key = gpt_env["GPT_IMAGE_API_KEY"]
    base_url = gpt_env.get("GPT_IMAGE_BASE_URL", "https://api.getgoapi.com")
    model_cfg = gpt_env.get("GPT_IMAGE_MODEL", "openai/gpt-image-2")

    env = dict(os.environ)
    env["GPT_IMAGE_API_KEY"] = api_key
    env["GPT_IMAGE_BASE_URL"] = base_url
    env["GPT_IMAGE_MODEL"] = model_cfg
    env["GPT_IMAGE_RESPONSE_FORMAT"] = "none"
    env["ARK_ALLOW_FORCE"] = "1"

    failed = []
    for look_id, prompt in PROMPTS.items():
        out = ROOT / META[look_id]["output"]
        print(f"=== Generating {look_id} ({META[look_id]['name']}) ...", flush=True)
        cmd = [
            sys.executable, str(CLI), "generate",
            "--prompt", prompt,
            "--output", str(out),
            "--model", "gpt-image-2",
            "--size", "1600x2848",
            "--force",
        ]
        r = subprocess.run(cmd, env=env, cwd=ROOT, capture_output=True, text=True)
        print(r.stdout[-3000:] if r.stdout else "", flush=True)
        if r.stderr:
            print("STDERR:", r.stderr[-2000:], flush=True)
        if r.returncode != 0 or not out.exists():
            failed.append(look_id)
            print(f"!!! {look_id} FAILED rc={r.returncode}", flush=True)
        else:
            print(f"OK {look_id} -> {out} ({out.stat().st_size} bytes)", flush=True)
    print("DONE failed:", failed or "none")


if __name__ == "__main__":
    main()
