#!/usr/bin/env python3
"""从 资产/场景卡片.md 权威 Prompt 生成 assets/seedream_batch_scenes.yaml（逐字一致）。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # dramas/边荒盐妇

# 场景 → 道具 TOS 参考图映射（道具卡片「关联场景」显著陈设道具）
PROP_REFS = {
    "SCENE-001": ["PROP-017"],   # 祖传盐耙
    "SCENE-004": ["PROP-010"],   # 木盐勺（笔筒）
    "SCENE-008": ["PROP-012"],   # 锁金匣
    "SCENE-009-b": ["PROP-014"], # 私盐总账（暗格）
    "SCENE-010": ["PROP-006"],   # 樟木箱
    "SCENE-012": ["PROP-005"],   # 黑秤（高悬）
    "SCENE-016": ["PROP-009"],   # 裴字盐铤（案头）
}

def main():
    card = (ROOT / "资产/场景卡片.md").read_text(encoding="utf-8")
    idx = card.find("# Seedream Prompts")
    if idx == -1:
        sys.exit("ERROR: Seedream Prompts section not found in 场景卡片.md")
    section = card[idx:]
    pattern = r"## (SCENE-[\w-]+)（[^）]*）\s*\n\n```\n(.*?)\n```"
    matches = re.findall(pattern, section, re.DOTALL)
    if len(matches) != 20:
        sys.exit(f"ERROR: expected 20 prompts, found {len(matches)}")

    cdn = json.loads((ROOT / "assets/props/cdn_urls.json").read_text(encoding="utf-8"))

    lines = ["items:"]
    for sid, prompt in matches:
        if not prompt.strip():
            sys.exit(f"ERROR: empty prompt for {sid}")
        esc = prompt.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  - id: "{sid}"')
        lines.append(f'    prompt: "{esc}"')
        refs = PROP_REFS.get(sid, [])
        if refs:
            lines.append("    image_urls:")
            for pid in refs:
                url = cdn[pid]["tos_url"]
                if not url.startswith("https://"):
                    sys.exit(f"ERROR: non-https tos_url for {pid}")
                lines.append(f'      - "{url}"')
        lines.append(f'    output: "assets/scenes/{sid}.png"')
    out = ROOT / "assets/seedream_batch_scenes.yaml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: wrote {out} with {len(matches)} items")
    # 验证：回读 YAML prompt 与卡片逐字一致
    import yaml  # type: ignore
    doc = yaml.safe_load(out.read_text(encoding="utf-8"))
    for it, (sid, prompt) in zip(doc["items"], matches):
        assert it["id"] == sid and it["prompt"] == prompt, f"MISMATCH {sid}"
    # image_urls 硬门控：全部 https
    for it in doc["items"]:
        for u in it.get("image_urls", []):
            assert u.startswith("https://"), f"non-https image_url in {it['id']}"
    print("VERIFY: prompts verbatim-identical to 场景卡片.md; all image_urls https ✅")

if __name__ == "__main__":
    main()
