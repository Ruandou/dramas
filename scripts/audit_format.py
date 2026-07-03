#!/usr/bin/env python3
"""Audit all 72 episode scripts for format consistency."""
import os, re, yaml, sys

base = "dramas/我妈退休后不装了"
results = []
Y = "Y"
N = "N"

for ep_num in range(1, 73):
    ep = f"EP{ep_num:02d}"
    fpath = f"{base}/剧本/{ep}/{ep}_剧本.md"
    if not os.path.exists(fpath):
        continue
    
    with open(fpath) as f:
        content = f.read()
    
    row = {"ep": ep}
    
    # Frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        try:
            fm = yaml.safe_load(fm_text) or {}
        except:
            fm = {}
    else:
        fm = {}
    
    row["season"] = Y if "season" in (fm or {}) and fm.get("season") else N
    row["prop_ids"] = Y if "prop_ids" in (fm or {}) else N
    sd = fm.get("seedance_defaults", {})
    if isinstance(sd, dict):
        row["gen_audio"] = Y if "generate_audio" in sd else N
        row["dur_sec"] = Y if "duration_sec" in sd else N
        row["prompt_suffix"] = Y if "prompt_suffix" in sd else N
        row["neg_prompt"] = Y if "negative_prompt" in sd else N
    else:
        row["gen_audio"] = row["dur_sec"] = row["prompt_suffix"] = row["neg_prompt"] = N
    
    missing = sum(1 for k in ["season","prop_ids","gen_audio","dur_sec","prompt_suffix","neg_prompt"] if row[k] == N)
    row["fm_missing"] = str(missing)
    
    # Sections
    row["yuanxinxi"] = Y if "元信息摘要" in content else N
    row["yusuan"] = Y if "时长预算表" in content else N
    row["tingdong"] = Y if "本集观众必须听懂" in content else N
    row["zhuanchang"] = Y if "转场" in content and "hard_cut" in content else N
    row["zhizuo"] = Y if "本集制作备注" in content else N
    row["zichan"] = Y if "本集资产" in content else N
    row["gouzi"] = Y if "结尾钩子" in content else N
    row["valid"] = Y if "VALIDATION" in content else N
    
    # Table columns
    header_match = re.search(r'\|.*镜.*\|', content)
    if header_match:
        header = header_match.group()
        cols = header.count('|') - 1
        row["cols"] = str(cols)
    else:
        cols = 0
        row["cols"] = "0"
    
    # Continuation rows
    cr_pattern = r'^\|(\s*\|){4,}\s*$'
    cr_count = len(re.findall(cr_pattern, content, re.MULTILINE))
    row["cr"] = str(cr_count) if cr_count > 0 else "-"
    
    results.append(row)

# Print table
header = f"| {'EP':>4} | {'列':>3} | season | prop_id | gen_au | dur_sec | prompt | neg_pr | 缺数 | 转场 | 听懂 | 备注 | 资产 | 续行 |"
sep = "|------|-----|--------|---------|--------|--------|--------|--------|------|------|------|------|------|------|"
print(header)
print(sep)
for r in results:
    print(f"| {r['ep']} | {r['cols']:>3} | {r['season']:>6} | {r['prop_ids']:>7} | {r['gen_audio']:>6} | {r['dur_sec']:>6} | {r['prompt_suffix']:>6} | {r['neg_prompt']:>5} | {r['fm_missing']:>4} | {r['zhuanchang']:>4} | {r['tingdong']:>4} | {r['zhizuo']:>4} | {r['zichan']:>4} | {r['cr']:>4} |")

# Summary
print()
total = len(results)
print(f"统计：共 {total} 集")
print()

# Count by missing count
for m in range(7):
    c = sum(1 for r in results if int(r['fm_missing']) == m)
    if c > 0:
        eps = [r['ep'] for r in results if int(r['fm_missing']) == m]
        print(f"  缺 {m} 字段：{c} 集 → {', '.join(eps)}")

print()
print("段缺失统计：")
for section, label in [("zhuanchang","转场"), ("tingdong","观众听懂"), ("zhizuo","制作备注")]:
    c = sum(1 for r in results if r[section] == N)
    eps = [r['ep'] for r in results if r[section] == N]
    print(f"  缺 {label}：{c} 集 → {', '.join(eps)}")

print()
print("续行空管子：")
for r in results:
    if r['cr'] != '-':
        print(f"  {r['ep']}：{r['cr']} 行")
