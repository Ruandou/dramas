# -*- coding: utf-8 -*-
import re

filepath = "/Users/leifu/Movies/dramas/dramas/满级影后她装新人/剧本/EP54/EP54_红毯归来.md"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find positions
seg01_marker = "**【SCENE-001】金像奖颁奖典礼·红毯入口**"
seg01_pos = content.find(seg01_marker)
old_seg02_pos = content.find("## SEG02 — 走红毯")

# Extract shots from current file
# Shot 1: in SEG01 table
shot1_start = content.find("| 1 | `EP54-S01`", seg01_pos)
shot1_end = content.find("\n", shot1_start)
shot1_line = content[shot1_start:shot1_end]

# Shot 2: in SEG01 table (after shot 1)
shot2_start = content.find("| 2 |", shot1_end)
shot2_end = content.find("\n", shot2_start)
shot2_line = content[shot2_start:shot2_end]

# Shot 3: in old SEG02 table
shot3_start = content.find("| 3 |", old_seg02_pos)
shot3_end = content.find("\n", shot3_start)
shot3_line = content[shot3_start:shot3_end]

# Shot 4: in old SEG02 table
shot4_start = content.find("| 4 |", shot3_end)
shot4_end = content.find("\n", shot4_start)
shot4_line = content[shot4_start:shot4_end]

# Build new content
# Part 1: Everything before and including the SEG01 table header
header_table_end = content.find("|------|---------|------|------|------|------|------|------|------|------|------|-----------|", seg01_pos)
header_end = content.find("\n", header_table_end) + 1

new_content = content[:header_end]
new_content += shot1_line + "\n"
new_content += "\n> ⏱ Segment时长：8s ｜ 镜头数：1\n"
new_content += "\n---\n"
new_content += "\n## SEG02 — 登场·走红毯（蓄力式·登场→惊艳）\n"
new_content += "\n**（续）**\n"
new_content += "\n| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |\n"
new_content += "|------|---------|------|------|------|------|------|------|------|------|------|-----------|\n"
new_content += shot2_line + "\n"
new_content += shot3_line + "\n"
new_content += "\n> ⏱ Segment时长：12s ｜ 镜头数：2\n"
new_content += "\n---\n"
new_content += "\n## SEG03 — 红毯全景（蓄力式·热议→震撼）\n"
new_content += "\n**（续）**\n"
new_content += "\n| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |\n"
new_content += "|------|---------|------|------|------|------|------|------|------|------|------|-----------|\n"
new_content += shot4_line + "\n"
new_content += "\n> ⏱ Segment时长：6s ｜ 镜头数：1\n"

# Add content after old SEG02 table
seg02_table_end = content.find("\n\n> ⏱", shot4_end)
seg02_dur_line = content[seg02_table_end:content.find("\n", seg02_table_end+1)]
# Find next segment start
remainder_start = content.find("## SEG03", old_seg02_pos)
remainder = content[remainder_start:]

# Renumber
remainder = remainder.replace("## SEG03 — 方芷晴在场", "## SEG04 — 方芷晴在场", 1)
remainder = remainder.replace("## SEG04 — 陆景深的注视", "## SEG05 — 陆景深的注视", 1)
remainder = remainder.replace("## SEG05 — 红毯采访", "## SEG06 — 红毯采访", 1)
remainder = remainder.replace("## SEG06 — 震撼全场", "## SEG07 — 震撼全场", 1)

# Fix SEG07 duration
remainder = remainder.replace(
    "> ⏱ Segment时长：11s ｜ 镜头数：2\n\n---\n\n## 结尾钩子",
    "> ⏱ Segment时长：12s ｜ 镜头数：2\n\n---\n\n## 结尾钩子", 1)

# Fix shot 12: 6->5
remainder = remainder.replace(
    "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 6 |",
    "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 5 |", 1)

# Fix SEG05 duration (old SEG04, shots 7(6)+8(6)=12, currently says 11s)
remainder = remainder.replace(
    "> ⏱ Segment时长：11s ｜ 镜头数：2\n\n---\n\n## SEG06 — 红毯采访",
    "> ⏱ Segment时长：12s ｜ 镜头数：2\n\n---\n\n## SEG06 — 红毯采访", 1)

new_content += remainder

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify
for m in re.finditer(r'(## SEG\d+ .*?)\n', new_content):
    print(f"  {m.group(1)}")
for m in re.finditer(r'> ⏱ Segment时长：(\d+)s ｜ 镜头数：(\d+)', new_content):
    print(f"  {m.group(1)}s, {m.group(2)} shots")

# Calculate total
total = sum(int(m.group(1)) for m in re.finditer(r'> ⏱ Segment时长：(\d+)s', new_content))
print(f"Total: {total}s")
