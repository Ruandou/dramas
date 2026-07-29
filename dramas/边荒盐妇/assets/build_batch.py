#!/usr/bin/env python3
"""从 资产/角色卡片.md 解析 46 条 Look Prompt，生成 seedream_batch_characters.yaml。
Prompt 逐字取自卡片（权威来源）。image_urls 映射：
  PROP-### → assets/props/cdn_urls.json tos_url
  CHAR-*-L## → looks TOS URL（Phase B 依赖，提交前需 Phase A 已上传）
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "资产/角色卡片.md"
PROPS = json.load(open(ROOT / "assets/props/cdn_urls.json"))
LOOK_URL = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/边荒盐妇/{}.png"

text = CARD.read_text(encoding="utf-8").splitlines()
items = []
i = 0
title_re = re.compile(r"^\*\*`(CHAR-[A-Za-z0-9-]+)`(?:[^*]*)\*\*（([^）]*)）")
while i < len(text):
    m = title_re.match(text[i])
    if m:
        look_id, note = m.group(1), m.group(2)
        # 找下一条 "> " prompt 行
        j = i + 1
        while j < len(text) and not text[j].startswith("> "):
            j += 1
        prompt = text[j][2:].strip()
        refs = re.findall(r"(PROP-\d+|CHAR-[A-Za-z0-9-]+-L\d+)", note)
        urls = []
        for r in refs:
            if r.startswith("PROP-"):
                u = PROPS.get(r, {}).get("tos_url")
                if not u:
                    sys.exit(f"FATAL: {look_id} 引用 {r} 无 tos_url")
                urls.append(u)
            else:
                urls.append(LOOK_URL.format(r))
        phase = "B" if any(u.startswith("https://") and "/looks/" in u for u in urls) else "A"
        items.append({
            "id": look_id,
            "phase": phase,
            "prompt": prompt,
            "image_urls": urls,
            "output": f"assets/looks/{look_id}.png",
        })
        i = j + 1
    else:
        i += 1

assert len(items) == 46, f"expect 46, got {len(items)}"
a = [x for x in items if x["phase"] == "A"]
b = [x for x in items if x["phase"] == "B"]
print(f"total={len(items)}  phaseA={len(a)}  phaseB={len(b)}")
for x in b:
    print("  B:", x["id"], "refs:", x["image_urls"])
# 校验：衍生 prompt 必含 SAME
for x in b:
    pr = x["prompt"]
    if not ("SAME person" in pr or "SAME child" in pr or x["id"] in ("CHAR-001-L03",)):
        print("  WARN no-SAME:", x["id"])
out = {"model_hint": "seedream", "size": "1600x2848", "ratio": "9:16", "items": items}
dest = ROOT / "assets/seedream_batch_characters.yaml"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("written:", dest)
