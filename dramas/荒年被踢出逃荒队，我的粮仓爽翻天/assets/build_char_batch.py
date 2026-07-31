#!/usr/bin/env python3
"""从 资产/角色卡片.md 逐字提取 36 条定妆 Prompt，组装 seedream_batch_characters.yaml。
- [REF-PREFIX]/[REF-SUFFIX] 展开为全文
- L01 道具参考图 → assets/props/cdn_urls.json 的 tos_url
- L02+ image_urls 留空占位（L01 TOS 上传后桥接）
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "资产/角色卡片.md"
PROPS = json.loads((ROOT / "assets/props/cdn_urls.json").read_text())
try:
    LOOKS = json.loads((ROOT / "assets/looks/cdn_urls.json").read_text())
except FileNotFoundError:
    LOOKS = {}

text = CARD.read_text()

# REF-PREFIX / REF-SUFFIX 展开
m_pre = re.search(r"通用前缀（下称 \[REF-PREFIX\]）：`([^`]+)`", text)
m_suf = re.search(r"通用后缀（下称 \[REF-SUFFIX\]）：`([^`]+)`", text)
PRE, SUF = m_pre.group(1), m_suf.group(1)

# 提取 header + code block
pattern = re.compile(r"^\*\*(CHAR-[A-Z0-9-]+-L\d{2})[^\n]*?\*\*（?([^\n]*)\n```text\n(.*?)\n```", re.M | re.S)
items = []
for m in pattern.finditer(text):
    cid, header_rest, prompt = m.group(1), m.group(2), m.group(3).strip()
    prompt = prompt.replace("[REF-PREFIX]", PRE).replace("[REF-SUFFIX]", SUF)
    # 参考图注记解析
    header_full = text[m.start():text.find("\n", m.start())]
    prop_refs = re.findall(r"(PROP-\d{3}(?:-[a-z])?)", header_full)
    is_l02 = not cid.endswith("-L01")
    based_on = None
    image_urls = []
    if is_l02:
        bm = re.search(r"(CHAR-\d{3}-L01)", header_full)
        based_on = bm.group(1) if bm else None
        # L02+ 桥接：L01 TOS URL 作面部参考（硬门控）
        if based_on and based_on in LOOKS and LOOKS[based_on].get("tos_url"):
            image_urls.append(LOOKS[based_on]["tos_url"])
        # L02 附加道具参考（如有）
        for p in prop_refs:
            if p in PROPS:
                image_urls.append(PROPS[p]["tos_url"])
    else:
        for p in prop_refs:
            if p in PROPS:
                image_urls.append(PROPS[p]["tos_url"])
            else:
                print(f"WARN: {cid} 引用 {p} 不在 cdn_urls.json", file=sys.stderr)
    items.append(dict(id=cid, prompt=prompt, based_on=based_on, image_urls=image_urls))

# 校验
assert len(items) == 36, f"expect 36, got {len(items)}"
l02s = [i for i in items if i["based_on"]]
assert len(l02s) == 6, f"expect 6 L02+, got {len(l02s)}: {[i['id'] for i in l02s]}"
for i in items:
    assert "NOT anime" in i["prompt"], i["id"]
    assert "[REF-" not in i["prompt"], i["id"]
    for u in i["image_urls"]:
        assert u.startswith("https://"), (i["id"], u)
    if i["based_on"]:
        # L02+ 硬门控：必须有 L01 TOS 参考图 + SAME person 指令
        assert i["image_urls"], f"{i['id']} 缺 L01 TOS 参考图（硬门控）"
        assert "SAME person as the reference image" in i["prompt"], f"{i['id']} 缺 SAME person 指令"

def yq(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

out = ["# seedream_batch_characters.yaml — 执行配置（权威源：资产/角色卡片.md）",
       "# L02+ image_urls 为空，待 L01 TOS 上传后桥接",
       "defaults:",
       "  model: doubao-seedream-5-0-lite-260128",
       '  size: "1600x2848"',
       "items:"]
for i in items:
    out.append(f"  - id: {yq(i['id'])}")
    if i["based_on"]:
        out.append(f"    based_on: {yq(i['based_on'])}")
    out.append(f"    prompt: {yq(i['prompt'])}")
    if i["image_urls"]:
        out.append("    image_urls:")
        for u in i["image_urls"]:
            out.append(f"      - {yq(u)}")
    elif i["based_on"]:
        out.append("    image_urls: []  # ← 桥接 L01 TOS URL 后方可生成")
    out.append(f"    output: \"assets/looks/{i['id']}.png\"")
(ROOT / "assets/seedream_batch_characters.yaml").write_text("\n".join(out) + "\n")
print(f"OK: 36 items ({len(l02s)} L02+ pending bridge)")
for i in items:
    refs = i["image_urls"] or (["<L01-bridge-pending>"] if i["based_on"] else [])
    print(f"  {i['id']}: refs={len(refs)} {'(' + ','.join(r.split('/')[-1] for r in i['image_urls']) + ')' if i['image_urls'] else ''}")
