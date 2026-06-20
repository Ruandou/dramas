# -*- coding: utf-8 -*-
import re

filepath = "/Users/leifu/Movies/dramas/dramas/满级影后她装新人/剧本/EP54/EP54_红毯归来.md"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Current issue: SEG01 has shots 1(8s) + 2(6s) = 14s in one table
# Need to split: shot 1 stays in SEG01, shots 2-3 go to SEG02, 
# shot 4 to SEG03, then renumber rest

# Step 1: Fix SEG01 table - remove shot 2 from SEG01's table
# Current SEG01 table has shots 1 and 2. Need to split.
old_table = "| 1 | `EP54-S01` | `SCENE-001` | `CHAR-GRP-09` | `—` | 全景 | 8 | `t2v` | 固定镜头 | 金像奖红毯全景——铺天盖地的镁光灯闪烁，记者群（CHAR-GRP-09）挤在红毯两侧，长枪短炮对准入口方向。红毯从入口一直延伸到剧院大门，两旁是黑色围栏和媒体的闪光灯巨墙。红毯上空悬挂着金色的金像奖标志灯牌 | （无对白，[镁光灯闪烁声·记者群嘈杂声·快节奏背景音乐]） |\n| 2 | `EP54-S02` | `SCENE-001` | `CHAR-001` | `CHAR-001-L04` | 中景 | 6 | `i2v_ref` | 镜头跟随 | 苏念晚出现在红毯入口——她穿着白色拖地礼服（`PROP-009`），丝绸缎面在聚光灯下泛着珍珠般的光泽。水晶耳饰在灯光下闪烁。她的长发披散在肩上，一侧挽到耳后露出精致的耳环。她站在红毯入口，微微停顿——看着前方那条通往剧院大门的红毯。她的表情平静中带着一抹难以言喻的光彩 | **CHAR-GRP-09**[记者群·嘈杂]：「苏念晚！是苏念晚！」**CHAR-GRP-09**[记者·高声]：「看这边！苏念晚——！」（快门声密集）**CHAR-001**[内心]：「十年前我穿着这条裙子走上红毯，以为那是一切的开始。」（停顿·迈步）「今天——我穿着同一条裙子，重新开始。」 |"

# Replace with just shot 1 in SEG01's table
new_table_shot1 = "| 1 | `EP54-S01` | `SCENE-001` | `CHAR-GRP-09` | `—` | 全景 | 8 | `t2v` | 固定镜头 | 金像奖红毯全景——铺天盖地的镁光灯闪烁，记者群（CHAR-GRP-09）挤在红毯两侧，长枪短炮对准入口方向。红毯从入口一直延伸到剧院大门，两旁是黑色围栏和媒体的闪光灯巨墙。红毯上空悬挂着金色的金像奖标志灯牌 | （无对白，[镁光灯闪烁声·记者群嘈杂声·快节奏背景音乐]） |"

shot2_content = "| 2 | `EP54-S02` | `SCENE-001` | `CHAR-001` | `CHAR-001-L04` | 中景 | 6 | `i2v_ref` | 镜头跟随 | 苏念晚出现在红毯入口——她穿着白色拖地礼服（`PROP-009`），丝绸缎面在聚光灯下泛着珍珠般的光泽。水晶耳饰在灯光下闪烁。她的长发披散在肩上，一侧挽到耳后露出精致的耳环。她站在红毯入口，微微停顿——看着前方那条通往剧院大门的红毯。她的表情平静中带着一抹难以言喻的光彩 | **CHAR-GRP-09**[记者群·嘈杂]：「苏念晚！是苏念晚！」**CHAR-GRP-09**[记者·高声]：「看这边！苏念晚——！」（快门声密集）**CHAR-001**[内心]：「十年前我穿着这条裙子走上红毯，以为那是一切的开始。」（停顿·迈步）「今天——我穿着同一条裙子，重新开始。」 |"

shot3_content = "| 3 | `EP54-S03` | `SCENE-001` | `CHAR-001` | `CHAR-001-L04` | 近景 | 6 | `i2v_ref` | 镜头跟随 | 苏念晚从容地走红毯。她的步伐不急不缓，每一步都踩在十年前走过的同一位置。白色礼服的裙摆在她身后优雅地拖曳过红毯。两侧快门声像暴雨般密集，闪光灯在她身上投下连绵不断的光。她微微侧头，对着镜头露出一个淡然而坚定的微笑 | **CHAR-001**[内心]：「十年前他们让我离开了这个舞台。」（停下脚步·面对镜头）「今天我回来了。（微笑）不是来复仇的。」（停顿·目光从容）「是来拿回属于我的东西。」 |"

shot4_content = "| 4 | `EP54-S04` | `SCENE-001` | `CHAR-GRP-09`, `CHAR-001` | `CHAR-001-L04` | 全景 | 6 | `i2v_ref` | 镜头拉远 | 全景镜头——苏念晚站在红毯中央，白色礼服在红色地毯和黑色人群的映衬下格外耀眼。她身边空出了一小圈，像所有人都在为她让路。远处剧院大门上方，金色的金像奖标志在灯光下闪闪发光 | **CHAR-GRP-09**[记者·激动]：「她穿的是十年前封后那条同款白裙！」**CHAR-GRP-09**[另一个记者]：「天哪——同款！这是故意的！」**CHAR-GRP-09**[远处]：「热搜已经爆了！#苏念晚红毯回归#冲上第一！」 |"

# Build the new structure from scratch
# Find the position of SEG01 content
seg01_marker = "**【SCENE-001】金像奖颁奖典礼·红毯入口** · **夜** · **外景**"
seg01_start = content.find(seg01_marker)
seg01_header_end = content.find("|------|---------|------|------|------|------|------|------|------|------|------|-----------|", seg01_start)
seg01_table_end = content.find("\n\n> ⏱ Segment时长", seg01_header_end)

# Find the old SEG02 start
seg02_old_start = content.find("## SEG02 — 走红毯", seg01_table_end)

# Build the new segment structure
new_segments = f"""**【SCENE-001】金像奖颁奖典礼·红毯入口** · **夜** · **外景**

| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |
|------|---------|------|------|------|------|------|------|------|------|------|-----------|
{new_table_shot1}

> ⏱ Segment时长：8s ｜ 镜头数：1

---

## SEG02 — 登场·走红毯（蓄力式·登场→惊艳）

**（续）**

| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |
|------|---------|------|------|------|------|------|------|------|------|------|-----------|
{shot2_content}
{shot3_content}

> ⏱ Segment时长：12s ｜ 镜头数：2

---

## SEG03 — 红毯全景（蓄力式·热议→震撼）

**（续）**

| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |
|------|---------|------|------|------|------|------|------|------|------|------|-----------|
{shot4_content}

> ⏱ Segment时长：6s ｜ 镜头数：1

---

## SEG04 — 方芷晴在场（刺探式·冰封→交锋）"""

# Replace the content from SEG01 scene marker to old SEG02 header
old_section = content[seg01_start:seg02_old_start]
print(f"Replacing from char {seg01_start} to {seg02_old_start}")
print(f"Old section length: {len(old_section)}")

content = content[:seg01_start] + new_segments + content[seg02_old_start + len("## SEG02 — 走红毯（独白递进·回忆→回归）"):]

# Now renumber remaining segments
renumbers = [
    ("SEG03 — 方芷晴在场", "SEG04 — 方芷晴在场"),
    ("SEG04 — 陆景深的注视", "SEG05 — 陆景深的注视"),
    ("SEG05 — 红毯采访", "SEG06 — 红毯采访"),
    ("SEG06 — 震撼全场", "SEG07 — 震撼全场"),
]

for old_name, new_name in renumbers:
    count = content.count(old_name)
    if count > 0:
        content = content.replace(old_name, new_name, count)
        print(f"Renamed '{old_name}' to '{new_name}' ({count} occurrences)")
    else:
        print(f"WARNING: '{old_name}' not found!")

# Fix shot 12: 6→5 to make SEG07 = 7+5=12s
old_shot12 = "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 6 |"
new_shot12 = "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 5 |"
if old_shot12 in content:
    content = content.replace(old_shot12, new_shot12, 1)
    print("Shot 12: 6→5")
else:
    print("WARNING: Shot 12 not found")

# Fix SEG07 segment duration: 11→12s (shots 11(7)+12(5)=12)
old_dur = "> ⏱ Segment时长：11s ｜ 镜头数：2\n\n---\n\n## 结尾钩子"
new_dur = "> ⏱ Segment时长：12s ｜ 镜头数：2\n\n---\n\n## 结尾钩子"
if old_dur in content:
    content = content.replace(old_dur, new_dur, 1)
    print("SEG07 duration: 11→12s")
else:
    print("WARNING: SEG07 duration not found")

# Fix SEG05 duration (was SEG04 old): shots 7(6)+8(6)=12s, currently says 11s
old_dur5 = "> ⏱ Segment时长：11s ｜ 镜头数：2\n\n---\n\n## SEG06 — 红毯采访"
new_dur5 = "> ⏱ Segment时长：12s ｜ 镜头数：2\n\n---\n\n## SEG06 — 红毯采访"
if old_dur5 in content:
    content = content.replace(old_dur5, new_dur5, 1)
    print("SEG05 duration: 11→12s")
else:
    print("WARNING: SEG05 duration not found - searching...")
    # Search for what's around SEG05
    idx = content.find("SEG05 —")
    if idx >= 0:
        print(f"Context around SEG05: ...{content[idx-50:idx+80]}...")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n=== FINAL VERIFICATION ===")
for m in re.finditer(r'(## SEG\d+ .*?)\n', content):
    print(f"  {m.group(1)}")
for m in re.finditer(r'> ⏱ Segment时长：(\d+)s ｜ 镜头数：(\d+)', content):
    print(f"  Segment: {m.group(1)}s, {m.group(2)} shots")
# -*- coding: utf-8 -*-
import re

filepath = "/Users/leifu/Movies/dramas/dramas/满级影后她装新人/剧本/EP54/EP54_红毯归来.md"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Current state after sed edits:
# SEG01: shot 1 (8s)
# SEG02: shots 3-4 (6+6=12s) - but actually shots 2 and 3 are in SEG01's table
# Need to restructure to have:
# SEG01: shot 1 (8s) single - 红毯全景
# SEG02: shots 2-3 (6+6=12s) - 登场+走红毯  
# SEG03: shot 4 (6s) single - 红毯全景反应
# SEG04: shots 5-6 (5+7=12s) - 方芷晴在场
# SEG05: shots 7-8 (6+6=12s) - 陆景深注视
# SEG06: shots 9-10 (6+6=12s) - 采访
# SEG07: shots 11-12 (7+6=13s) - need to fix to 12s

# First, let's see the current structure
print("Current SEG headers:")
for m in re.finditer(r'## (SEG\d+).*?\n', content):
    print(f"  {m.group(1)}")

# Split SEG01 into SEG01(shot1) + new SEG02(shots2-3)
# The old SEG02(shots 3-4) becomes SEG03(shot4 only)

# Find the boundary markers
seg01_end = "> ⏱ Segment时长：8s ｜ 镜头数：1"
seg02_start = "## SEG02 — 走红毯"

# Build new SEG02 content  
new_seg02 = """---

## SEG02 — 登场·走红毯（蓄力式·登场→惊艳）

**（续）**

| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |
|------|---------|------|------|------|------|------|------|------|------|------|-----------|
| 2 | `EP54-S02` | `SCENE-001` | `CHAR-001` | `CHAR-001-L04` | 中景 | 6 | `i2v_ref` | 镜头跟随 | 苏念晚出现在红毯入口——她穿着白色拖地礼服（`PROP-009`），丝绸缎面在聚光灯下泛着珍珠般的光泽。水晶耳饰在灯光下闪烁。她的长发披散在肩上，一侧挽到耳后露出精致的耳环。她站在红毯入口，微微停顿——看着前方那条通往剧院大门的红毯。她的表情平静中带着一抹难以言喻的光彩 | **CHAR-GRP-09**[记者群·嘈杂]：「苏念晚！是苏念晚！」**CHAR-GRP-09**[记者·高声]：「看这边！苏念晚——！」（快门声密集）**CHAR-001**[内心]：「十年前我穿着这条裙子走上红毯，以为那是一切的开始。」（停顿·迈步）「今天——我穿着同一条裙子，重新开始。」 |
| 3 | `EP54-S03` | `SCENE-001` | `CHAR-001` | `CHAR-001-L04` | 近景 | 6 | `i2v_ref` | 镜头跟随 | 苏念晚从容地走红毯。她的步伐不急不缓，每一步都踩在十年前走过的同一位置。白色礼服的裙摆在她身后优雅地拖曳过红毯。两侧快门声像暴雨般密集，闪光灯在她身上投下连绵不断的光。她微微侧头，对着镜头露出一个淡然而坚定的微笑 | **CHAR-001**[内心]：「十年前他们让我离开了这个舞台。」（停下脚步·面对镜头）「今天我回来了。（微笑）不是来复仇的。」（停顿·目光从容）「是来拿回属于我的东西。」 |

> ⏱ Segment时长：12s ｜ 镜头数：2

---

## SEG03 — 红毯全景（蓄力式·热议）

**（续）**

| 镜号 | shot_id | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 运镜 | 画面 | 对白/备注 |
|------|---------|------|------|------|------|------|------|------|------|------|-----------|
| 4 | `EP54-S04` | `SCENE-001` | `CHAR-GRP-09`, `CHAR-001` | `CHAR-001-L04` | 全景 | 6 | `i2v_ref` | 镜头拉远 | 全景镜头——苏念晚站在红毯中央，白色礼服在红色地毯和黑色人群的映衬下格外耀眼。她身边空出了一小圈，像所有人都在为她让路。远处剧院大门上方，金色的金像奖标志在灯光下闪闪发光 | **CHAR-GRP-09**[记者·激动]：「她穿的是十年前封后那条同款白裙！」**CHAR-GRP-09**[另一个记者]：「天哪——同款！这是故意的！」**CHAR-GRP-09**[远处]：「热搜已经爆了！#苏念晚红毯回归#冲上第一！」 |

> ⏱ Segment时长：6s ｜ 镜头数：1

---

## SEG04 — 方芷晴在场（刺探式·冰封→交锋）"""

# Now the old SEG03 becomes SEG05, SEG04→SEG06, SEG05→SEG07, SEG06→SEG08
# And we need to handle the segment boundaries

print("\nApplying restructure...")

# Step 1: Replace SEG01 end + old SEG02 start with new SEG02 + SEG03
old = seg01_end + "\n\n---\n\n" + seg02_start
content = content.replace(old, seg01_end + new_seg02, 1)

# Step 2: Renumber remaining segments
# Old SEG03 → SEG04... wait, we've consumed the old SEG02. The next segment is old SEG03
renumbers = [
    ("SEG03 — 方芷晴在场", "SEG04 — 方芷晴在场"),
    ("SEG04 — 陆景深的注视", "SEG05 — 陆景深的注视"),
    ("SEG05 — 红毯采访", "SEG06 — 红毯采访"),
    ("SEG06 — 震撼全场", "SEG07 — 震撼全场"),
]

for old_name, new_name in renumbers:
    content = content.replace(old_name, new_name, 1)

# Step 3: Fix SEG07 (was SEG06) - shots 11(7)+12(6)=13s
# Need to reduce one shot. Reduce shot 12: 6→5, so 7+5=12
old_shot12 = "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 6 | `i2v_ref` | 镜头拉远 | 大远景镜头——苏念晚白色礼服的身影消失在剧场大门内，灯光在她身后合拢。另一侧的方芷晴独自站在原地，周围空无一人，她紧握着手包，指甲嵌进掌心。红毯上的镁光灯还在继续闪烁，但焦点已经转移——所有人都在谈论刚刚那个瞬间 | **CHAR-003**[独自站在角落里·低声·咬牙切齿]：「你会没事的……对。你当然会没事。」（停顿·声音颤抖）「那我呢……」**CHAR-003**[转身·急促离去]：「不能输……不能输在这里。」 |"
new_shot12 = "| 12 | `EP54-S12` | `SCENE-001` | `CHAR-001`, `CHAR-003` | `CHAR-001-L04`, `CHAR-003-L01` | 全景 | 5 | `i2v_ref` | 镜头拉远 | 大远景镜头——苏念晚白色礼服的身影消失在剧场大门内，灯光在她身后合拢。另一侧的方芷晴独自站在原地，周围空无一人，她紧握着手包，指甲嵌进掌心。红毯上的镁光灯还在继续闪烁，但焦点已经转移——所有人都在谈论刚刚那个瞬间 | **CHAR-003**[独自站在角落里·低声·咬牙切齿]：「你会没事的……对。你当然会没事。」（停顿·声音颤抖）「那我呢……」**CHAR-003**[转身·急促离去]：「不能输……不能输在这里。」 |"

if old_shot12 in content:
    content = content.replace(old_shot12, new_shot12, 1)
    print("Shot 12 reduced from 6 to 5")
else:
    print("WARNING: Could not find shot 12")

# Step 4: Update SEG07 segment duration
content = content.replace("> ⏱ Segment时长：11s ｜ 镜头数：2\n\n---\n\n## 结尾钩子", "> ⏱ Segment时长：12s ｜ 镜头数：2\n\n---\n\n## 结尾钩子", 1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Restructure complete!")
print("\nNew SEG headers:")
for m in re.finditer(r'## (SEG\d+).*?\n', content):
    print(f"  {m.group(0).strip()}")
print("\nSegment durations:")
for m in re.finditer(r'> ⏱ Segment时长：(\d+)s.*?(\d+)', content):
    print(f"  {m.group(0).strip()}")
