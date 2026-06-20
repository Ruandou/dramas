# -*- coding: utf-8 -*-
import re

filepath = "/Users/leifu/Movies/dramas/dramas/满级影后她装新人/剧本/EP54/EP54_红毯归来.md"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find positions
seg01_marker = "**【SCENE-001】金像奖颁奖典礼·红毯入口**"
seg01_pos = content.find(seg01_marker)
old_seg02_pos = content.find("## SEG02 — 走红毯")

print(f"SEG01 at: {seg01_pos}, Old SEG02 at: {old_seg02_pos}")

# Extract shot2 line from the file
shot2_start = content.find("| 2 | `EP54-S02`", seg01_pos, old_seg02_pos)
shot2_end = content.find("\n", shot2_start)
shot2_line = content[shot2_start:shot2_end]
print(f"Shot 2 line: {shot2_line[:80]}...")

# Extract shot3 line
shot3_start = content.find("| 3 | `EP54-S03`", seg01_pos, old_seg02_pos)
shot3_end = content.find("\n", shot3_start)
shot3_line = content[shot3_start:shot3_end]
print(f"Shot 3 line: {shot3_line[:80]}...")

# Extract shot4 line (in old SEG02 table)
shot4_start = content.find("| 4 | `EP54-S04`", old_seg02_pos)
shot4_end = content.find("\n", shot4_start)
shot4_line = content[shot4_start:shot4_end]
print(f"Shot 4 line: {shot4_line[:80]}...")

# Now build the new content
# Part 1: Everything before the SEG01 table
header_table_end = content.find("|------|---------|------|------|------|------|------|------|------|------|------|-----------|", seg01_pos)
header_end = content.find("\n", header_table_end) + 1

# Part 2: shot 1 only (from SEG01)
shot1_start = content.find("| 1 | `EP54-S01`", seg01_pos)
shot1_end = content.find("\n", shot1_start)
shot1_line = content[shot1_start:shot1_end]

# Part 3: segment duration line for SEG01
seg1_dur_start = content.find("> ⏱ Segment时长：8s", shot1_end)
seg1_dur_end = content.find("\n", seg1_dur_start)

# Part 4: old SEG02 header
seg2_header_line = content[old_seg02_pos:content.find("\n", old_seg02_pos)]

# Build new content
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

# Now add the rest after old SEG02 (the old SEG02 has been replaced by our SEG03)
# The old SEG02 content ends at the next SEG marker
remainder_start = content.find("## SEG03", old_seg02_pos)
if remainder_start < 0:
    # Maybe there's no SEG03 yet, try the next --- separator
    remainder_start = content.find("\n---\n\n", old_seg02_pos + 50)
    if remainder_start > 0:
        remainder_start = content.find("\n---\n", remainder_start + 5)
        remainder_start = content.find("\n", remainder_start + 5)

remainder = content[remainder_start:]

# Renumber: SEG03 -> SEG04, SEG04 -> SEG05, SEG05 -> SEG06, SEG06 -> SEG07
remainder = remainder.replace("## SEG03 — 方芷晴在场", "## SEG04 — 方芷晴在场", 1)
remainder = remainder.replace("## SEG04 — 陆景深的注视", "## SEG05 — 陆景深的注视", 1)
remainder = remainder.replace("## SEG05 — 红毯采访", "## SEG06 — 红毯采访", 1)
remainder = remainder.replace("## SEG06 — 震撼全场", "## SEG07 — 震撼全场", 1)

# Update SEG07 duration from 11s to 12s (shots 11(7)+12(5)=12s)
remainder = remainder.replace(
    "> ⏱ Segment时长：11s ｜ 镜头数：2\n\n---\n\n## 结尾钩子",
    "> ⏱ Segment时长：12s ｜ 镜头数：2\n\n---\n\n## 结尾钩子", 1)

# Update shot 12 from 6s to 5s (to make SEG07 = 7+5=12s)
remainder = remainder.replace(
    "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 6 |",
    "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 5 |", 1)

new_content += remainder

# Write
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n=== VERIFICATION ===")
for m in re.finditer(r'(## SEG\d+ .*?)\n', new_content):
    print(f"  {m.group(1)}")
for m in re.finditer(r'> ⏱ Segment时长：(\d+)s ｜ 镜头数：(\d+)', new_content):
    print(f"  {m.group(1)}s, {m.group(2)} shots")
