#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHAR-004~015 + CHAR-GRP-01~11 L01/L02 generator (Stage 3b-G 批次 2).
Reads GPT_IMAGE_API_KEY from .cursor/mcp.json without printing it.
Run from workspace root:
  python3 dramas/剑宗小祖宗/assets/run_char_batch2_gen.py --group l01-batch1
  python3 dramas/剑宗小祖宗/assets/run_char_batch2_gen.py --group l02
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts_3b_batch2 import PROMPTS, META, REF_URLS_L01, PRIORITY_GROUPS, MESH_EXEMPT

ROOT = Path("/Users/lei/Movies/demo1")
CLI = ROOT / "mcps/gpt-image/scripts/gpt_image.py"
PROJECT = "dramas/剑宗小祖宗"
LOOKS_CDN = ROOT / PROJECT / "assets/looks/cdn_urls.json"


def load_env():
    with open(ROOT / ".cursor/mcp.json") as f:
        mcp = json.load(f)
    gpt_env = mcp["mcpServers"]["gpt-image"]["env"]
    env = dict(os.environ)
    env["GPT_IMAGE_API_KEY"] = gpt_env["GPT_IMAGE_API_KEY"]
    env["GPT_IMAGE_BASE_URL"] = gpt_env.get("GPT_IMAGE_BASE_URL", "https://api.getgoapi.com")
    env["GPT_IMAGE_MODEL"] = gpt_env.get("GPT_IMAGE_MODEL", "openai/gpt-image-2")
    env["GPT_IMAGE_RESPONSE_FORMAT"] = "none"
    env["ARK_ALLOW_FORCE"] = "1"
    return env


def l01_tos_url(look_id: str) -> str | None:
    """从 looks/cdn_urls.json 读取已上传 L01 的 TOS 永久 URL（供 L02 参考图）。"""
    if not LOOKS_CDN.is_file():
        return None
    with open(LOOKS_CDN) as f:
        reg = json.load(f)
    entry = reg.get(look_id)
    if not entry:
        return None
    url = entry.get("tos_url") or entry.get("cdn_url")
    if not url or "X-Tos-Expires" in url or "X-Tos-Signature" in url:
        return None
    return url


def refs_for(look_id: str) -> list[str]:
    """计算该形象的参考图 URL 列表。"""
    if look_id in REF_URLS_L01:
        return REF_URLS_L01[look_id]
    # L02：从 cdn_urls.json 取对应 L01 的 TOS 永久 URL
    base = look_id.rsplit("-L02", 1)[0] + "-L01"
    url = l01_tos_url(base)
    if url:
        return [url]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", required=True, choices=list(PRIORITY_GROUPS.keys()))
    ap.add_argument("--ids", default=None, help="逗号分隔，只处理指定 look_id")
    args = ap.parse_args()

    env = load_env()
    look_ids = PRIORITY_GROUPS[args.group]
    if args.ids:
        wanted = {x.strip() for x in args.ids.split(",") if x.strip()}
        look_ids = [x for x in look_ids if x in wanted]

    failed = []
    for look_id in look_ids:
        out = ROOT / META[look_id]["output"]
        if out.exists() and args.group != "l02":
            # L01 已存在则跳过（幂等）；L02 需要强制重新生成（若已存在也应覆盖）
            print(f"SKIP {look_id} (already exists)", flush=True)
            continue
        prompt = PROMPTS[look_id]
        refs = refs_for(look_id)
        print(f"=== Generating {look_id} ({META[look_id]['name']}) refs={refs} ...", flush=True)
        cmd = [
            sys.executable, str(CLI), "generate",
            "--prompt", prompt,
            "--output", str(out),
            "--model", "gpt-image-2",
            "--size", "1600x2848",
            "--force",
        ]
        for u in refs:
            cmd += ["--image-url", u]
        r = subprocess.run(cmd, env=env, cwd=ROOT, capture_output=True, text=True)
        print(r.stdout[-4000:] if r.stdout else "", flush=True)
        if r.stderr:
            print("STDERR:", r.stderr[-2000:], flush=True)
        if r.returncode != 0 or not out.exists():
            failed.append(look_id)
            print(f"!!! {look_id} FAILED rc={r.returncode}", flush=True)
        else:
            print(f"OK {look_id} -> {out} ({out.stat().st_size} bytes)", flush=True)
    print(f"DONE group={args.group} failed={failed or 'none'}", flush=True)


if __name__ == "__main__":
    main()
