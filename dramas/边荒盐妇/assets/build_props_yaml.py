#!/usr/bin/env python3
"""从 资产/道具卡片.md 逐字提取道具 Prompt（EN）组装 seedream_batch_props.yaml"""
import re, json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
card = (root / "资产/道具卡片.md").read_text(encoding="utf-8")

# 按 PROP 段切分
sections = re.split(r"\n## (PROP-\d{3})", card)
items = []
for i in range(1, len(sections), 2):
    pid = sections[i]
    body = sections[i + 1]
    m = re.search(r"\*\*道具 Prompt（EN）\*\*：\s*\n\s*\n```\n(.*?)\n```", body, re.S)
    if m:
        items.append((pid, m.group(1).strip()))

expected = [f"PROP-{n:03d}" for n in list(range(1, 21)) + [22]]
got = [p for p, _ in items]
assert got == expected, f"mismatch: {got}"

lines = ["items:"]
for pid, prompt in items:
    lines.append(f'  - id: "{pid}"')
    lines.append(f"    prompt: {json.dumps(prompt, ensure_ascii=False)}")
    lines.append(f'    output: "assets/props/{pid}.png"')
(root / "assets/seedream_batch_props.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"OK: {len(items)} items -> assets/seedream_batch_props.yaml")
