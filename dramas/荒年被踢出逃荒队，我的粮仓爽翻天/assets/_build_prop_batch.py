#!/usr/bin/env python3
"""从 资产/道具卡片.md 权威提取 Seedream Prompt，组装 assets/seedream_batch_props.yaml。
保证 batch YAML 与卡片 Prompt 逐字一致（prop-designer Step 5）。"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARD = ROOT / "资产" / "道具卡片.md"
OUT = ROOT / "assets" / "seedream_batch_props.yaml"

text = CARD.read_text(encoding="utf-8")
sections = re.split(r"(?=^### PROP-\d{3})", text, flags=re.M)

items = []
skipped = []
for sec in sections:
    m = re.match(r"^### (PROP-\d{3})", sec)
    if not m:
        continue
    pid = m.group(1)
    ref_m = re.search(r"\| 参考图 \| `(待生成|场景内置|角色内置)`", sec)
    if not ref_m:
        print(f"ERROR: {pid} 无参考图分类", file=sys.stderr); sys.exit(2)
    cls = ref_m.group(1)
    if cls != "待生成":
        skipped.append((pid, cls))
        continue
    # 找到 “**道具 Prompt（EN）**：” 之后的所有 ```text 代码块及其前导标签行
    pm = sec.split("**道具 Prompt（EN）**：", 1)
    if len(pm) < 2:
        print(f"GATE FAIL: {pid} 缺少道具 Prompt", file=sys.stderr); sys.exit(2)
    body = pm[1]
    blocks = re.findall(r"(?:^([ABC])（[^\n]*?）：\s*\n)?```text\n(.*?)\n```", body, flags=re.S | re.M)
    if not blocks:
        print(f"GATE FAIL: {pid} Prompt 代码块为空", file=sys.stderr); sys.exit(2)
    for label, prompt in blocks:
        prompt = prompt.strip().replace("\n", " ")
        if not prompt:
            print(f"GATE FAIL: {pid} 空 Prompt", file=sys.stderr); sys.exit(2)
        suffix = {"": "", "A": "", "B": "-b", "C": "-c"}[label]
        iid = pid + suffix
        items.append({"id": iid, "prompt": prompt, "output": f"assets/props/{iid}.png"})

# 门控汇总
gen_props = sorted({it["id"][:8] for it in items})
print(f"GENERATE props: {len(gen_props)} | images: {len(items)} | skipped: {skipped}")
if len(gen_props) != 27:
    print("GATE FAIL: 待生成道具数 != 27", file=sys.stderr); sys.exit(2)

def q(s):
    return json.dumps(s, ensure_ascii=False)

lines = ["items:"]
for it in items:
    lines.append(f"  - id: {q(it['id'])}")
    lines.append(f"    prompt: {q(it['prompt'])}")
    lines.append(f"    output: {q(it['output'])}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"written: {OUT} ({len(items)} items)")
for it in items:
    zh = re.findall(r'"([^"]*[\u4e00-\u9fff][^"]*)"', it["prompt"])
    sc = "Simplified Chinese" in it["prompt"]
    print(f"  {it['id']}: SimpChinese={'Y' if sc else '-'} zh_text={zh if zh else '-'}")
