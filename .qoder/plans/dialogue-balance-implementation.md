# Plan: Implement Narrative Balance Rules (Dialogue vs. Monologue)

## Context

The scene-writer agent currently over-encourages inner monologue as the primary narrative tool ("独白即叙事"), treating monologue and dialogue as interchangeable in all density metrics. Audited scripts show 80-93% of spoken lines are inner monologue (超雄重生1995 EP01 = 83%, 布衣账房 EP01 = 93%), contradicting industry best practice (红果教程EP09: "对白是绝对主力；OS和VO应尽量少用"). Design decisions were captured in memory but never written to agent files.

**Goal**: Rebalance the agent system so dialogue drives the narrative and monologue fills gaps that dialogue cannot.

---

## Task 1: Reframe Core Principles in scene-writer.md

**File**: `.qoder/agents/scene-writer.md`

### 1a. Rewrite "对白工艺" section (lines 19-29)

Replace:
- `独白即叙事：主角内心独白/自述是最高效的 AI 短剧叙事手段`
- With: `对白驱动，独白补盲区：对白是叙事主力（≥40% spoken lines），独白仅用于对白无法承载的信息（隐秘心思、潜台词夹层、推理过程）`

Update bullet points:
- Add "对白比例" as a hard metric: `对白占比 ≥ 40%（角色间的实际对话），独白+旁白 ≤ 60%`
- Change "金句设计" to note golden lines should prefer dialogue over monologue
- Add "多角色优先": `每集 ≥ 2 个说话角色，单人独白场景 ≤ 2 段/集`

### 1b. Rewrite "AI 生成适配原则" section (lines 48-53)

Replace:
- `对白/独白是 AI 短剧的第一生产力` → `对白是 AI 短剧的第一生产力`
- `内心独白使用场景：推理、回忆、计划、情感纠结、信息总结、悬念引导——这些都应大量使用独白` → Restrict monologue to specific use cases with justification requirement
- Add: `独白不是叙事的默认选项——当一段信息可以通过两个角色的对话传递时，必须用对话而非独白`

---

## Task 2: Add New Hard Rules in scene-writer.md

**File**: `.qoder/agents/scene-writer.md` (约束条件 section, after Rule 36)

Add 3 new rules:

### Rule 37: Dialogue-to-Monologue Ratio
```
37. **对白占比下限**：全集所有 spoken lines 中，角色间实际对白（非独白、非旁白）占比 **≥ 40%**。
    低于 40% = 叙事过度依赖独白，必须将部分独白改写为角色对话。
    判定方法：统计标记为 `[内心]` / `[内心独白]` / `旁白` 的行数 vs 角色对白行数。
    独白豁免：以下独白不计入比例限制——
    (a) 紧跟对白后的潜台词独白（揭示"嘴上说的 ≠ 心里想的"，≤ 1 句）
    (b) 推理/发现类独白（侦探推理、数学计算等画面无法表达的内容）
    (c) EP01 开场穿越/重生确认段（≤ 2 段）
```

### Rule 38: Minimum Speaking Characters
```
38. **最少说话角色数**：每集必须有 **≥ 2 个不同 CHAR-### 说话角色**（含群演 CHAR-GRP-##）。
    如果剧情需要主角独处（如推理、修炼），必须引入至少 1 个对话对象（回忆中的声音、电话对方、路过的配角等）。
    单人独白段（仅 1 个 CHAR 说话且全部为独白）全集 **≤ 2 段**。
```

### Rule 39: Hook Zone Dialogue Requirement
```
39. **Hook Zone 对白优先**：Hook Zone（EP02+ 前 15 秒 / EP01 前 20 秒）必须包含至少 1 句角色对白（非独白）。
    开场用独白铺陈背景是被禁止的（Rule "Hook Zone 绝对禁止" 已覆盖）。
    Hook Zone 的对白应以冲突、质问、揭秘等高张力形式出现。
```

---

## Task 3: Update Rule 36(e) in scene-writer.md

**File**: `.qoder/agents/scene-writer.md`

Change `Rule 36(e)`:
- From: `独白连续上限 2 句：角色连续独白不超过 2 句后必须有中断`
- To: `独白连续上限 1 句：角色连续独白不超过 1 句后必须有中断（对白回应/动作行/画面切换/他人打断）。超过 1 句连续独白 = 演讲模式，需拆分。豁免：Rule 37 豁免清单中的独白不受此限。`

---

## Task 4: Update Self-Check Rules in scene-writer.md

**File**: `.qoder/agents/scene-writer.md` (Segment 自检规则 section)

### 4a. Update self-check item 9 (line 238)
Add: `该段是否有独白？如果有，该独白是否可以通过引入对话对象改为对白？`

### 4b. Update self-check item 10 (line 239)
Change: `(a) 台词+独白+旁白总行数 ≥ 50; (b) 总行数 ÷ 总时长(分钟) ≥ 20`
Add: `(c) 对白占比 ≥ 40%（对白行数 ÷ 全部 spoken lines 行数）。不满足 → 找到独白最密集的 SEG，将其中 1-2 句独白改写为角色对话。`

---

## Task 5: Add Dialogue-Ratio Check to script-reviewer.md

**File**: `.qoder/agents/script-reviewer.md` (维度 7 section)

Add to 审查子项:
```
- **对白/独白比例审计**：统计全集中角色对白行数 vs 独白+旁白行数。对白占比 < 40% = 叙事失衡，维度 7 ≤ 3 分。对白占比 < 25% = 严重失衡，维度 7 ≤ 2 分。
- **说话角色数检查**：统计全集中不同 CHAR-### 说话角色数。< 2 个 = 叙事结构缺陷，维度 7 ≤ 2 分。
- **单人独白段计数**：统计仅 1 个角色说话且全部为独白的 segment 数量。> 2 段 = 过度依赖独白，维度 7 扣 1 分。
```

Update score anchors to include ratio:
- Score 5: add `对白占比 ≥ 50%`
- Score 3: add `对白占比 25-40%`
- Score 2: add `对白占比 < 25%`
- Score 1: add `对白占比 < 15% 或全剧仅 1 个说话角色`

---

## Task 6: Add Dialogue-Ratio Gate to drama-director.md

**File**: `.qoder/agents/drama-director.md` (G4 验证门控 table, around line 460)

Add row to G4 table:
```
| 对白占比 | 对白（非独白/旁白）行数 ÷ 全部 spoken lines ≥ 40% | 低于 40% → 请求 scene-writer 将独白最密集的 SEG 改写为角色对话 |
| 说话角色数 | ≥ 2 个不同 CHAR-### 说话角色 | 仅 1 个 → 请求 scene-writer 引入对话对象（电话/回忆/配角） |
```

---

## Task 7: Add Character Count Guideline to story-architect.md

**File**: `.qoder/agents/story-architect.md`

Add to 自检 3 (角色一致性, around line 512):
```
- 每集大纲中至少标注 2 个参与对话/互动的角色（scene-writer 需要对话对象）
- 如某集大纲仅涉及 1 个角色独处，需在设计阶段补充互动角色（信使、电话对象、回忆中的人物等）
```

---

## Verification

After all edits:
1. **Grep validation**: Confirm new keywords (`对白占比`, `≥ 40%`, `≥ 2 个.*说话角色`, `Hook Zone.*对白`) appear in all 4 target files
2. **Cross-reference check**: Confirm rule numbers in scene-writer.md are sequential (37, 38, 39) and don't conflict with existing rules
3. **Semantic consistency**: Confirm the reframed principle in scene-writer.md ("对白驱动，独白补盲区") no longer contains "独白即叙事"
4. **Memory update**: Update the existing memory entries to reflect that the rules are now implemented (not just "designed")
