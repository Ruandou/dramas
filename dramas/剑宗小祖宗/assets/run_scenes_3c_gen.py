#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3c-G helper: generate SCENE-003~010 via gpt_image.py CLI.
Reads prompts from 资产/场景卡片.md (source of truth) -> assets/scenes/SCENE-###.png
Env: GPT_IMAGE_API_KEY from .cursor/mcp.json; GPT_IMAGE_RESPONSE_FORMAT=none; ARK_ALLOW_FORCE=1.
submitting/blocked placeholder -> retry with --force."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/lei/Movies/demo1")
PROJ = ROOT / "dramas/剑宗小祖宗"
CARD = PROJ / "资产/场景卡片.md"
SCENES_DIR = PROJ / "assets/scenes"
CLI = ROOT / "mcps/gpt-image/scripts/gpt_image.py"

TARGETS = [f"SCENE-{n:03d}" for n in range(3, 11)]


def load_mcp_env() -> dict:
    d = json.load(open(ROOT / ".cursor/mcp.json", encoding="utf-8"))
    env = {}
    gi = d["mcpServers"]["gpt-image"]["env"]
    env["GPT_IMAGE_API_KEY"] = gi.get("GPT_IMAGE_API_KEY", "")
    env["GPT_IMAGE_BASE_URL"] = gi.get("GPT_IMAGE_BASE_URL", "")
    env["GPT_IMAGE_MODEL"] = gi.get("GPT_IMAGE_MODEL", "")
    return env


def extract_prompts() -> dict:
    text = CARD.read_text(encoding="utf-8")
    sections = re.split(r"\n## (SCENE-\d+) ", text)
    prompts = {}
    for i in range(1, len(sections), 2):
        sid = sections[i]
        body = sections[i + 1]
        m = re.search(r"\|\s*英文 Prompt\s*\|\s*`([^`]+)`\s*\|", body)
        if m:
            prompts[sid] = m.group(1).strip()
    return prompts


def run_generate(prompt: str, out_rel: str, env: dict, force: bool = False) -> dict:
    cmd = [sys.executable, str(CLI), "generate",
           "--prompt", prompt,
           "--model", "gpt-image-2",
           "--size", "1600x2848",
           "--output", out_rel,
           "--project-root", "dramas/剑宗小祖宗"]
    if force:
        cmd.append("--force")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)
    try:
        data = json.loads(r.stdout) if r.stdout.strip() else {}
    except Exception:
        data = {"raw": r.stdout[-2000:], "stderr": r.stderr[-2000:]}
    return data


def main() -> int:
    env = dict(os.environ)
    env.update(load_mcp_env())
    env["GPT_IMAGE_RESPONSE_FORMAT"] = "none"
    env["ARK_ALLOW_FORCE"] = "1"
    if not env.get("GPT_IMAGE_API_KEY"):
        print("ERROR: GPT_IMAGE_API_KEY missing")
        return 1
    prompts = extract_prompts()
    missing = [s for s in TARGETS if s not in prompts]
    if missing:
        print("MISSING PROMPTS:", missing)
        return 1
    out = {}
    for sid in TARGETS:
        out_path = SCENES_DIR / f"{sid}.png"
        if out_path.exists():
            out[sid] = {"status": "exists", "output": str(out_path)}
            print(f"[{sid}] SKIP: output already exists")
            continue
        prompt = prompts[sid]
        out_rel = str(out_path.relative_to(ROOT))
        print(f"[{sid}] generating ...")
        data = run_generate(prompt, out_rel, env)
        status = data.get("status", "unknown")
        if status in ("ok", "skip"):
            out[sid] = {"status": status, "output": str(out_path), "detail": {k: data.get(k) for k in ("task_id", "cdn_url") if k in data}}
            print(f"[{sid}] OK ({status})")
        elif status in ("submitting", "blocked"):
            print(f"[{sid}] status={status}; retrying with --force ...")
            data2 = run_generate(prompt, out_rel, env, force=True)
            status2 = data2.get("status", "unknown")
            out[sid] = {"status": status2, "output": str(out_path), "retry": {k: data2.get(k) for k in ("task_id", "cdn_url", "status") if k in data2}, "first": {k: data.get(k) for k in ("status", "reason") if k in data}}
            print(f"[{sid}] retry status={status2}")
        else:
            out[sid] = {"status": status, "output": str(out_path), "detail": data}
            print(f"[{sid}] status={status}")
    (SCENES_DIR / "generation_report_3c.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
