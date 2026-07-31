#!/usr/bin/env python3
"""Stage 3c 场景参考图生成执行器：从 资产/场景卡片.md 提取 Prompt（权威源）→ 调用 ark_seedream_image.py。
幂等：已存在的输出文件自动跳过（迭代修复时删除对应 png 再跑）。"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/lei/Movies/demo1")
DRAMA = REPO / "dramas/我的金手指是盗版的"
CARD = DRAMA / "资产/场景卡片.md"
CLI = REPO / "mcps/volc-ark/scripts/ark_seedream_image.py"
OUT_DIR = DRAMA / "assets/scenes"

# 卡片中 17 个代码块的固定顺序（与场景卡片 v1.1 一致）
ORDER = [
    "SCENE-001", "SCENE-002", "SCENE-002-night", "SCENE-003", "SCENE-004",
    "SCENE-005", "SCENE-006", "SCENE-006-night", "SCENE-007", "SCENE-007-night",
    "SCENE-008", "SCENE-009", "SCENE-010", "SCENE-011", "SCENE-012",
    "SCENE-013", "SCENE-014",
]

# 道具融入：传 TOS URL（唯一允许的 image_urls 来源）
PROP_URLS = json.loads((DRAMA / "assets/props/cdn_urls.json").read_text())
IMAGE_REFS = {
    "SCENE-002": [PROP_URLS["PROP-001"]["tos_url"]],
    "SCENE-002-night": [PROP_URLS["PROP-001"]["tos_url"]],
    "SCENE-005": [PROP_URLS["PROP-005"]["tos_url"]],
}


def load_ark_key() -> str:
    data = json.loads((REPO / ".cursor/mcp.json").read_text())
    env = (data.get("mcpServers") or {}).get("volc-ark", {}).get("env", {})
    key = (env.get("ARK_API_KEY") or env.get("VOLC_ARK_API_KEY") or "").strip()
    if not key:
        sys.exit("ARK_API_KEY 缺失")
    return key


def extract_prompts() -> list[str]:
    text = CARD.read_text(encoding="utf-8")
    blocks = re.findall(r"```\n(.*?)\n```", text, flags=re.S)
    if len(blocks) != len(ORDER):
        sys.exit(f"Prompt 块数不符：{len(blocks)} != {len(ORDER)}")
    for i, b in enumerate(blocks):
        if not b.strip():
            sys.exit(f"第 {i} 个 Prompt 为空（门控失败）")
    return [b.strip() for b in blocks]


def main() -> None:
    import os
    os.environ["ARK_API_KEY"] = load_ark_key()
    only = set(sys.argv[1:])  # 可传场景 ID 只跑子集
    prompts = extract_prompts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    calls = 0
    for sid, prompt in zip(ORDER, prompts):
        if only and sid not in only:
            continue
        out = OUT_DIR / f"{sid}.png"
        if out.exists():
            print(f"[skip] {sid} 已存在", flush=True)
            continue
        cmd = [sys.executable, str(CLI), "generate",
               "--prompt", prompt, "--output", str(out), "--ratio", "9:16"]
        for url in IMAGE_REFS.get(sid, []):
            if not url.startswith("https://"):
                sys.exit(f"{sid} image_url 非 https TOS URL，阻断")
            cmd += ["--image-url", url]
        print(f"[gen ] {sid} refs={len(IMAGE_REFS.get(sid, []))} ...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        calls += 1
        ok = out.exists()
        print(f"[{'done' if ok else 'FAIL'}] {sid} rc={r.returncode}", flush=True)
        if not ok:
            print(r.stdout[-800:], r.stderr[-800:], flush=True)
    print(f"[total] 本次付费调用 {calls} 次", flush=True)


if __name__ == "__main__":
    main()
