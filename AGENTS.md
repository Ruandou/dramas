# AI 短剧制作流水线

本仓库采用 Agent 驱动的 7 阶段制作流水线，由 `drama-director`（总导演）统一调度。

> 完整 Agent 定义文件位于 `.qoder/agents/` 目录。

## Agent 定义索引

本仓库定义了 9 个专业 Agent，采用**单一真相源**架构：

| 位置 | 格式 | 用途 |
|------|------|------|
| `.qoder/agents/` | `.md` | 🔴 权威定义源（完整内容） |
| `.cursor/agents/` | `.md`（symlink） | 🟢 Cursor `/name` subagent 入口，指向 `.qoder/agents/` |
| `.zcode/agents/` | `.md`（**硬链接**） | 🟣 ZCode 子代理加载目录，硬链接回 `.qoder/agents/`（见下） |
| `.github/prompts/` | `.prompt.md` | 🔵 GitHub 工作流引用（链接指向权威源） |

在 Cursor Agent 对话中可用 `/drama-director`、`/scene-writer` 等显式调用 subagent（独立上下文窗口）；也可用自然语言「用 drama-director subagent …」委派。ZCode 中通过 `Agent` 工具的 `subagent_type` 参数以名称调用（如 `scene-writer`、`drama-director`）。

> **✅ ZCode 支持 markdown subagent（2026-06-29 逆向确认）**：ZCode 现版本**已原生支持** frontmatter + 提示词式 markdown subagent（与 Cursor 同模型），无需再转写 `.workflow.js`。加载逻辑（`zcode.cjs` 中 `loadZCodeAgentProfiles`）扫描两类目录的 `*.md`：
> - **user 级**：`~/.zcode/agents/`
> - **project 级**：`<仓库根>/.zcode/agents/` ← 本仓库落点
>
> frontmatter 强制 `name` + `description`，可选 `model / tools / disallowedTools / skills / permissionMode / maxTurns / color / background / mcpServers`；现有 9 个 agent 的 frontmatter 全部兼容，无需改内容。
>
> **关键约束 — 必须用硬链接，不能用 symlink**：加载器 `C8r` 用 `dirent.isFile()` 过滤目录条目，**符号链接的 `isFile()` 返回 false 会被静默跳过**。因此 `.zcode/agents/` 下必须放真实文件 inode。我们用硬链接（`ln` 不带 `-s`）而非软链接，使同一 inode 同时挂在两处路径：
> - 真相源仍唯一：`.qoder/agents/<name>.md`
> - `.zcode/agents/<name>.md` 与之共享 inode，编辑任一边立即同步，无需构建/同步脚本
> - 对 ZCode 的 `isFile()` 检查返回 true，可正常加载
>
> **维护方式**：新增/重命名 agent 时，在 `.qoder/agents/` 落稿后补一条硬链接即可：
> ```bash
> ln ".qoder/agents/<新agent>.md" ".zcode/agents/<新agent>.md"
> ```
> （删除时连同两端一起删。）
>
> **历史**：早期按「ZCode CLI 读 `.zcode/cli/agents/`」推测放的 symlink 占位已删除——实际加载器只看 `.zcode/agents/`（无 `cli` 段），且 symlink 被 `isFile()` 过滤，故该旧目录本就不参与加载。

### Agent 列表

| Agent | 角色 | 职责描述 |
|-------|------|---------|
| `drama-director` | 总导演 | 驱动完整制作流水线、管理门控、状态追踪 |
| `story-architect` | 故事架构师 | 86集故事大纲、情绪弧线、钩子矩阵设计 |
| `production-planner` | 制片结构注册师 | ID 系统建立、资产骨架、元数据提取 |
| `prop-designer` | 道具视觉设计师 | 道具参考图生成（Stage 3a，优先执行） |
| `character-designer` | 角色设计师 | 角色卡片填充、形象参考图生成（Stage 3b） |
| `scene-designer` | 场景设计师 | 场景参考图生成、道具融合（Stage 3c） |
| `scene-writer` | 分镜编剧 | 分集剧本编写、对白设计、分镜指导 |
| `segment-builder` | 分镜构建师 | YAML 生成、API 提交配置转换 |
| `script-reviewer` | 剧本审核师 | 质量门控（R1/R2）、合规审查 |

## 流水线阶段

> 自 2026-08-05 起运行**双轨制**：剧本轨（平台无关、零扣费、连续逐集）与制作轨（平台依赖、扣费、随时启动）独立推进、互不阻塞，仅通过「两轨交接协议」关联。

```
                        ┌─────────────────────────────────────────┐
                        │          共享基础设施（Part A）            │
                        │  初始化 → 门控通则 → 交接协议 → 工作计划    │
                        └─────────────────────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              │                                               │
  ┌───────────▼───────────┐                       ┌───────────▼───────────┐
  │   剧本轨（Part B）      │                       │   制作轨（Part C）      │
  │                       │                       │                       │
  │  Stage 1 → G1 → R1   │                       │  Stage 3a → 3b ∥ 3c  │
  │  Stage 2 → G2         │                       │  → G3                 │
  │  Stage 4 → G4 → R2   │── 标记「可制作」───────→│  Stage 5 → G5         │
  │  （逐集循环，不等待）    │    （交接协议）         │  Stage 6 → G6         │
  │                       │                       │  （对可制作集随时启动）  │
  └───────────────────────┘                       └───────────────────────┘
```

| Stage | Agent | 轨道 | 职责 | 核心产出 |
|-------|-------|------|------|----------|
| 1 | `story-architect`（故事架构师） | 剧本轨 | 86集故事大纲、情绪弧线、钩子矩阵 | `短剧剧本_<剧名>_86集.md` |
| 2 | `production-planner`（制片结构注册师） | 剧本轨 | ID 系统、资产骨架、外貌锚点、分段规则 | `制片规范.md` + `资产/` 骨架卡 |
| 3a | `prop-designer`（道具设计师） | 制作轨 | 道具视觉设计（3a-D 零扣费）→ 用户确认 → 参考图生成（3a-G 扣费） | `assets/props/` + CDN URLs |
| 3b | `character-designer`（角色设计师） | 制作轨 | 角色视觉设计（3b-D 零扣费）→ 用户确认 → 形象图生成（3b-G 扣费，使用道具参考图） | `资产/角色卡片.md` + `assets/looks/` |
| 3c | `scene-designer`（场景设计师） | 制作轨 | 场景视觉设计（3c-D 零扣费）→ 用户确认 → 参考图生成（3c-G 扣费，使用道具参考图） | `assets/scenes/` + CDN URLs |
| 4 | `scene-writer`（分镜编剧） | 剧本轨 | 分集剧本、镜头表（连续逐集，不等待制作） | `剧本/EP##/EP##_*.md` |
| 5 | `segment-builder`（分镜构建师） | 制作轨 | YAML 生成供 API 提交（对「可制作」集随时启动） | `剧本/EP##/EP##_shots.yaml` + `EP##_segments.yaml` |
| 6 | `drama-director`（总导演） | 制作轨 | 标题/封面/简介合规审查 | 发布就绪确认 |

> **🚫 双轨并行（2026-08-05 更新）**：流水线拆为**剧本轨**（平台无关、连续推进）与**制作轨**（平台依赖、随时启动）两条独立轨道：
> - **剧本轨**：scene-writer 按集**连续逐集**写作（一次一集，严禁批量/并行），每集经 Stage 4 → G4 → R2 剧本定稿门（G4 后即审、不等制作）定稿并标记「可制作」后，立即推进 EP(N+1)，**不等待该集 Stage 5 / G5 / 出片**。**剧本轨仅依赖 Stage 1+2 产物**（86集大纲 + 制片规范 + 骨架卡：CHAR-###/SCENE-###/PROP-###、语言画像草案、外貌锚点、voice_prompt），零扣费、零阻塞，不设中间阶段。
> - **制作轨**：对任意已标记「可制作」的集**独立随时启动**。Stage 3 内**设计先行**：3-D 设计（文字，零扣费）→ 逐设计师用户确认 → 3-G 生成（图片，扣费），用户可停在 3-D；3-G 完成后经素材就绪（C7）+ G3 增量验证 + 制作放行门（维度 6 视觉资产补审）→ 逐集转译 YAML → G5 → 出片，与剧本轨互不阻塞。
>
> 两轨各自内部均禁止批量/并行（违反「一次一集」硬红线 = 流程违规，产出作废）。完整规则见 `.qoder/agents/drama-director.md`「Part A3 两轨交接协议」「Part B6 剧本轨集数推进」「Part C10 制作轨集数推进」段及各 agent 约束条件。

**辅助角色**：
- `script-reviewer`（剧本审核师）：R1（大纲后）和 R2·剧本定稿门（单集剧本 G4 后即审）质量门控 + 制作放行门（维度 6 补审）
- `drama-director`（总导演）：流水线调度、门控判定、状态追踪

## 质量门控（Gate）

| 门控 | 位置 | 轨道 | 职责 |
|------|------|------|------|
| G1 | Stage 1 → Stage 2 | 剧本轨 | 大纲完整性校验 |
| G2 | Stage 2 → [Stage 4 ∥ Stage 3] | 两轨 | 制片体系 + ID 骨架 + 外貌锚点就绪 |
| G3 | [3a + 3b ∥ 3c] → 5 | 制作轨 | 道具/角色/场景资产就绪（不阻塞剧本轨） |
| G4 | Stage 4 后（剧本轨内） | 剧本轨 | 分集剧本合规性 |
| G5 | Stage 5 完成 | 制作轨 | YAML 合规校验 |
| G6 | Stage 5 → 发布 | 制作轨 | 元数据合规性 |

**审查节点**：
- **R1**（G1 之后）：`script-reviewer` 审查 86 集大纲，≥15/25 分放行
- **R2·剧本定稿门**（每集 G4 之后，不等 G3/G5）：`script-reviewer` 审查单集剧本（维度 1-5 + 7，满分 30），EP01 ≥24/30 硬门控，EP02+ ≥21/30 软门控（未过则暂停并报告、用户可 override 后带记录继续）；通过并 notes 清零 → 该集标记「可制作」，剧本轨推进下一集
- **制作放行门**（制作轨启动某集前，C7 素材就绪 + G3 增量验证后）：`script-reviewer` 补审维度 6（视觉资产审查，满分 5），≥4/5 硬门控，通过后制作轨启动该集 Stage 5

> **⚠️ notes 清零协议（2026-07-26 起强制）**：R1/R2 分数达标≠放行。审查判定只有两个终态：**PASS（clean）** 与 **FAIL**；「PASS with notes」是中间态，必须执行「源头修复（R1→大纲正文、R2→剧本正文）→ 同步下游文件 → director 实测验证 → reviewer 核销轮」循环，直到 notes 清零升级 PASS（clean）才可放行（循环上限 3 轮，超限升级用户）。题材属性/赛道同质化等无法文本修复的因素列「结构性观察」，不计 notes、不阻断。禁止把 notes 挂账给下游阶段后直接放行。详见 `.qoder/agents/script-reviewer.md`「判定终态与 notes 清零协议」。

> **📅 分制口径代差告知**：2026-06-30 前的历史审核报告（如 `dramas/布衣账房/`、`dramas/前任的弟弟是我的租客/` 等 `docs/审核报告_R2_*.md`）按旧 30 分制生成（EP01 ≥21/30 硬门控）。2026-06-30 至 2026-08-04 期间项目按 35 分制（EP01 ≥28/35、EP02+ ≥25/35）。自 2026-08-05 双轨改造起，R2 拆为「剧本定稿门」（30 分制：维度 1-5 + 7，EP01 ≥24/30、EP02+ ≥21/30）与「制作放行门」（5 分制：维度 6，≥4/5）。历史报告不改写，但跨项目比对时需注意分制代差。

## Agent 工作闭环原则（⚠️ 所有 Agent 强制执行）

所有 Agent 工作必须遵循**闭环验证**模式，不得跳过验证直接推进下一步：

```
Step → Verify → [有问题? → Fix → Verify (循环至干净)] → Next Step
```

**具体要求**：
1. **每步必验**：完成一个操作后，必须立即验证结果正确性（如：编辑后验证文件内容、生成后验证产出格式、合并后验证计数一致）
2. **有错必修**：验证发现任何问题，必须修复后重新验证，不得带着已知问题进入下一步
3. **干净才进**：只有验证通过（无问题）后，才能进入下一步骤
4. **证据可查**：验证结果必须有可追溯的证据（如 grep 计数、diff 对比、读取确认），不能仅凭"看起来对"

**流水线中的应用**：
- Stage 完成 → Gate 验证 → [问题? → 修复 → 重新 Gate] → Gate 通过 → 下一 Stage
- 多文件编辑：编辑文件 A → 验证 A → 编辑文件 B → 验证 B（不可攒批不验）
- 质量门控：G1-G6 和 R1-R2 是正式验证节点，但不替代步骤内的即时验证

## 时长红线（禁止数学游戏）⚠️ 对 scene-writer / segment-builder / drama-director 强制执行

> 以下规则来自生产事故复盘：大模型在剧本时长不够时倾向于"数学游戏"——直接给某几个镜头加 1s 或几秒凑数，内容不变，产出的视频是拖长的空镜/慢动作。剧本是整条流水线的真相源（scene-writer → segment-builder → 视频生成引擎按段扣费的视频生成），剧本凑数=后面全浪费，故必须从源头杜绝。

### 三条硬规则

1. **❌ 禁止纯加秒**：任何镜头 `duration_sec` 数字的修改，必须伴随对白/独白/画面的**实质性新增**。仅改数字不改内容 = 造假，整集作废重写。典型违规：某镜头 5s 改 8s 但对白/画面描述不变；加一个空镜但不带台词或叙事推进。**"实质性"判定**：新增对白须通过台词有效性测试（推进剧情/揭示角色/传递信息/建立关系/制造张力之一），加无功能感叹词/重复信息不算（详见 scene-writer Rule 25 + 台词有效性扫描（工作流程步骤 6 验证 #11）+ 密度公式 Rule 23）。
2. **时长不达标即重写整集**：剧本总时长低于或高于 `制片规范.md` → `episode_profile` 定义的合规区间（示例 standard-86: <75s/EP01<90s 或 >120s；长集项目以实际 episode_profile 为准）时，**不得**通过延长/拆分/加镜头等方式在原稿上补足。唯一路径：废弃当前稿 → 重做时长预算 → 从大纲重新展开整集。"只差几秒微调一下"的念头必须打消，不分差距大小，差 1s 也重写。
3. **重写前必须做时长预算**：重写（或首次写作）任何 SEG 正文前，先列时长预算表（每 SEG 场景/镜头数/单镜时长/SEG 时长），合计落合规区间后才动笔，争取一次写够，避免再次不够。

### 各 Agent 职责

| Agent | 职责 |
|-------|------|
| scene-writer | 写前做时长预算（步骤 4.5 场景级粗预算 + §3.5 SEG 级细预算，两阶段）；写后自检 5.5 回填实际时长与预算对比（闭环两阶段预算）；自检 1 总时长不达标即重写整集；禁止纯加秒；**重写上限 2 次（共 3 稿），仍不达标则升级 drama-director 诊断根因（可能是大纲场景容量不足，需回 story-architect）**。详见 `.qoder/agents/scene-writer.md` 自检 1 + 自检 5.5 + Rule 1 + 工作流程步骤 4.5 |
| segment-builder | Gate 1 发现时长不达标 → 报告要求 scene-writer 重写整集（非扩充）；发现疑似凑数（镜头时长与对白/画面不匹配）→ 标注 `suspected_padding` 并要求重写，不得放行 |
| drama-director | G4 时长不达标 → 要求 scene-writer 重写整集（非局部修正）；**接收 scene-writer 3 稿仍不达标的升级 → 诊断根因，必要时回退 story-architect 调整大纲场景容量**；禁止行为含"加秒数凑时长=造假" |

## Stage 3 视觉资产质量强制清单（⚠️ 对所有 Stage 3 Agent 和 director 强制执行）

以下规则来自生产事故复盘（"匿名坦白局"项目 5 类失败）。**所有 Stage 3 agent 执行前必须逐项检查**，director 在 G3 门控放行前必须验证。

### A. Prompt 设计自检（生成前 — agent 必须执行）

每个 prompt 逐条检查：
- [ ] **场景/道具人脸禁令**：场景和道具图中**严禁**出现任何人类面孔（含照片、画像、贴纸、屏幕显示等平面媒介）。人物由视频生成引擎（video_gen）阶段加入。角色卡要求"墙上挂照片"时，改用物品替代（名牌/奖状/标志性物件）
- [ ] **道具参考图自然锚点（2026-07-30 双事故复盘）**：图片生成引擎会把 `image_urls` 参考图**原样复制进画面**（该结论为 Seedream 实测，当前默认引擎 gpt-image 需以实际输出验证）。仅当 prompt 显式把道具绑定到自然物理锚点（held in hand / hanging at waist sash / parked on the floor beside X）并写明接触面时才可传道具参考图；镜头中不自然可见的道具一律文字描述、不传图（事故：残页参考图被平贴到角色胸口）
- [ ] **空间介词无歧义**：禁用 "at the head of the table" 类可读作"在桌面上"的歧义表述，必须显式命名支撑面（on the floor / on the tabletop）（事故：轮椅被摆上会议桌桌面）
- [ ] **文字语种**：场景/道具/角色物品（刻字玉佩、绣字长袍等）如需出现中文，必须写 `Simplified Chinese`，不能只写 `Chinese text`（会出繁体）
- [ ] **文字内容**：所有需要的标签、铭文、手写内容必须**完整拼出**在 prompt 中

### B. 道具交叉引用检查（生成前 — director 必须执行）

**先判定道具类别**：
- **固定陈设**（祭坛、武器架、牌匾等常驻物）→ 场景图中应含该道具，走下方交叉引用
- **情节道具**（襁褓、信件、兵器等随剧情出现/消失的物体）→ **严禁入场景底图**：场景图必须保持空场景，该道具由视频阶段 `shots.yaml` 的 `prop_urls` 传入锁定外观（2026-08-07 事故：SCENE-001 底图固化襁褓导致跨集穿帮 + 与基准时段不符）

**场景中出现固定陈设道具时**：
- [ ] 该道具图是否在 `image_urls` 中？
- [ ] 该道具是否已生成并上传对象存储（storage）？

**视频生成引擎（video_gen）阶段道具锁定**：
场景图本身不保证道具在视频中外观稳定——视频生成引擎可能改变场景中的物品。需要道具外观严格一致的镜头，**必须**在 `shots.yaml` 中将道具图作为独立参考图传入：
```yaml
assets:
  prop_urls:
    PROP-003: https://.../PROP-003.png   # 存储永久 URL（当前 TOS）
api:
  content_roles:
    - file: PROP-003
      role: reference_image
```
此机制确保同一道具（如电动车、服务器、手机）在所有镜头中外观不漂移。

### C. 串行 Stage 强制（G2→G3 门控）

**严格顺序，依赖边界处不得并行**：
```
Stage 3a（道具，含即生即传） → [验证 cdn_urls.json] → Stage 3b（角色）∥ Stage 3c（场景）
```
- 道具必须已上传对象存储（storage），角色/场景才能引用

### D. 生成后验证（每批次生成后立即执行）

1. [ ] **对象存储上传 + 更新 registry**（storage 能力，TOS 为当前默认引擎；CLI 路径见 `engine_registry.cli_path('storage')`）：`tos_upload.py sync --project-root dramas/<剧名>`
   （`sync` 内部已自动上传 + 更新 `cdn_urls.json`，等价于底层 `upload-dir` + `update-registry` 两步；与 prop/character/scene-designer 的命令一致）
2. [ ] **更新卡片状态**：道具卡片.md、角色卡片.md、场景卡片.md、形象索引.md 中所有 `待生成` → `✅ 已生成`
3. [ ] **更新工作计划.md** 流水线状态

### E. 场景/道具人脸禁令

场景参考图和道具参考图中**绝对禁止**出现任何人类面孔（含照片、画像、海报、贴纸、屏幕显示等平面媒介）。如制作规范或卡片要求“墙上挂某人照片”，**必须将其替换为物品**（如名牌、奖状、标志性物品）—— 不可试图通过 `image_urls` 传角色 L01 来做“人脸一致性”，这不可靠。

### F. L02+ 面部一致性硬门控

L02+ 衍生形象**必须**通过 `image_urls`（CLI: `--image-url`）传入对应角色 L01 的存储永久 URL（当前 TOS `tos_url`）作为面部参考图。

- [ ] **L01 参考图必须传入**：`image_urls` 包含 L01 的 `https://` 存储永久 URL，不得为空 `[]`
- [ ] **Prompt 必须包含面部一致性指令**："SAME person as the reference image"、"Keep the SAME face"
- [ ] **禁止仅靠文本 FACE ANCHOR**：图片生成引擎无法从文本描述复现同一张脸（该结论为 Seedream 实测，gpt-image 需以实际输出验证），即使一字不差的 FACE ANCHOR 也会生成不同人脸

**事故复盘**：《修仙界唯一的男人》CHAR-006-L02 首次生成时仅用文本 FACE ANCHOR（未传 L01 参考图），导致生成完全不同的人脸。重新生成时传入 L01 `--image-url` 后问题解决。

CLI 示例（当前默认引擎 gpt-image；CLI 路径随引擎，见 `mcps/shared/engine_registry.py`）：
```bash
python3 mcps/gpt-image/scripts/gpt_image.py generate \
  --image-url "https://drama-reference-images.tos-cn-beijing.volces.com/looks/<剧名>/CHAR-XXX-L01.png" \
  --prompt "The SAME person as the reference image..." \
  --output "dramas/<剧名>/assets/looks/CHAR-XXX-L02.png"
```

### G. 面部网格变体强制（视频生成引擎（video_gen）输入人脸过滤解法）

> 来自生产验证（2026-07-26，《满级师尊她装作刚入门》EP01 全集 10/10 段）：照片级写实人脸参考图会被 ARK 以 `InputImageSensitiveContentDetected.PrivacyInformation` 确定性拒绝（HTTP 400 不建单不扣费）。解法：用 `script/add_face_mesh.py` 在面部叠加 AR 风格三角网格后即可通过，且**网格不会被复现到成片、面部一致性保持**（男女角色、特写/全景均验证）。轻度 CG 风格化重渲染**无效**（仍被拒）。

规则：
- [ ] **生成时机**：character-designer 在每张含可见人脸的 L01/L02+ 确认后，立即生成 `-mesh.png` 变体，并随「即生即传」流程一并上传对象存储（storage）
- [ ] **命名**：`CHAR-###-L##-mesh.png`，群演为 `CHAR-GRP-##-L01-mesh.png`（群演同样适用本规则）；与原图同目录（`assets/looks/`），同步注册 cdn_urls.json
- [ ] **登记凭据**：生成或豁免结论必须登记到 `资产/形象索引.md` 对应行（`✅ mesh已生成` / `mesh豁免（剪影）` / `mesh豁免（背影）`）；下游 segment-builder 与 G3 均以此登记为准，**无登记视为缺口**，不得自行猜测是否豁免
- [ ] **使用边界**：仅视频生成引擎（video_gen）提交（shots/segments YAML 的 `look_urls`）用 mesh 版；图片生成 L02+ 衍生、对外展示仍用原图
- [ ] **豁免**：逆光剪影、背影等无可见人脸的形象图不触发过滤，无需 mesh 版（需登记豁免，见上）
- [ ] **根治并行**：向平台申请 AIGC 白名单后可逐步退场

### H. 事故速查表（跳过后会发生什么）

| 跳过此项 | 结果 |
|---------|------|
| 道具参考图自然锚点/空间介词检查 | 道具图被原样平贴进画面（残页贴胸口）、道具落在荒诞位置（轮椅上会议桌），视频生成引擎继承缺陷至成片 |
| 场景/道具人脸禁令 | 场景中出现错误角色面孔、西方面孔或无意义人脸（SCENE-009 教授照） |
| 文字语种检查 | 简体内容出现繁体文字（PROP-011 商业计划书） |
| 道具交叉引用检查 | 道具与场景不匹配 |
| 串行门控 | 道具/角色/场景并行生成，无法使用 `image_urls` 交叉引用 |
| 生成后验证 | 卡片状态卡在“待生成”，下游阶段缺少存储永久 URL |
| L02+ 面部一致性门控 | L02 生成完全不同的人脸（CHAR-006-L02 事故），必须重新生成 |
| 面部网格变体 | 视频生成引擎提交被人脸过滤 HTTP 400 拦截，整集无法开工（满级师尊 EP01 事故，后由 mesh 方案解决） |

## ID 格式

- **镜头 ID**：`EP##-S##`（两段式：集号-镜号）
- **角色 ID**：`CHAR-###`
- **群演 ID**：`CHAR-GRP-##` / `CHAR-GRP-##-L01` — 每个不同视觉角色独立 ID + L01（按需创建，无上限，仅受 API 参考图配额每 segment ≤6 张约束）。ID 由 `production-planner` 统一分配；`scene-writer` 写作中发现未分配群演时用 `[待补：描述]` 占位 + 「待补群演清单」，触发「集间群演回补子循环」由 `production-planner` 分配 ID + `character-designer` 回补 L01（详见各 agent 定义）
- **场景 ID**：`SCENE-###`
- **道具 ID**：`PROP-###`

## 项目文件结构

> ⚠️ **新建项目时必须用 `script/init_drama_project.sh <剧名>` 创建骨架**，不要手写 `mkdir`。
> 仓库根目录名是 `dramas`、子目录也叫 `dramas/`，模型极易把"项目根 `dramas/<剧名>`"与"仓库根 `dramas`"搞混 → 写错位置污染 `assets/`、产生孤儿文件、下游找不到归属导致重复扣费。
> 脚本内置路径守门（强制 `dramas/` 前缀、防重名、防路径穿越），CLI 也已守门 `--project-root` 拒绝被传成仓库根（见 `assert_valid_drama_project_root`）。

```
dramas/<剧名>/
├── 资产/              ← 角色卡片.md, 形象索引.md, 场景卡片.md, 道具卡片.md, 声音卡片.md
├── 剧本/EP01/         ← 分集剧本 + 分镜脚本 + YAML
├── assets/            ← AI 生成素材
│   ├── generated/     ← 视频素材（视频生成引擎输出）
│   ├── looks/         ← 角色形象参考图（图片生成输出）
│   └── scenes/        ← 场景参考图
├── 制片规范.md        ← 项目"宪法"（ID 系统、分段规则）
├── 工作计划.md        ← 流水线状态追踪
└── 短剧剧本_<剧名>_86集.md  ← 86集大纲
```

> **注**：`资产/`（中文）= 卡片 markdown（角色卡片/场景卡片/道具卡片/形象索引/声音卡片）；
> `assets/`（英文）= 生成的二进制素材（props/looks/scenes 下的 png + cdn_urls.json）。
> 两者是不同目录，不是别名。

## MCP 工具链

> 🔴 **执行前先读规范（硬约束，2026-08-07 事故固化）**：任何环节动手前，必须**先读**对应权威规则再执行——`docs/制片规范模板.md`（后期合成必读 §七 声音/§七B 字幕与叠加层）、项目 `制片规范.md`、`AGENTS.md` 强制清单。**禁止凭直觉/经验直接开工**（事故链：字幕用错工具漏出场卡、--force 未测即用、reconcile 一轮不跑、情节道具入底图，全部是"先干后查"导致）。执行顺序：读规则 → 确认适用项 → 执行 → 对照规则自检 → 才可交付。

> 🔌 **引擎注册表**：图片/视频生成/存储按「能力」引用，当前默认引擎由 `mcps/shared/engine_registry.py` 统一解析：`image_gen`（图片生成，默认 **gpt-image**，备选 seedream）、`video_gen`（视频生成，默认 seedance，备选 kling）、`storage`（对象存储/参考图永久托管，默认 **tos**，备选可扩展）。切换引擎改注册表或设 `IMAGE_GEN_ENGINE` / `VIDEO_GEN_ENGINE` / `STORAGE_ENGINE` 环境变量即可，agent 提示词无需改。视频默认参数（model/ratio/resolution/duration_sec 等）由 `video_defaults()` 解析；存储桶/永久 URL 由 `storage_info()` / `storage_url()` 解析；各能力 CLI 路径由 `cli_path()` 解析。

| 功能 | MCP 服务 | 工具 | 扣费 |
|------|----------|------|------|
| 图片生成（默认 image_gen） | `gpt-image` | `gpt_image_generate` / `gpt_image_batch` | **是** |
| 图片生成（备选） | `volc-ark` | `ark_seedream_generate` / `ark_seedream_batch` | **是** |
| 图片托管 | `imgbb` | `imgbb_upload` | 否 |
| 视频生成（默认 video_gen） | `volc-ark` | `ark_seedance_create` / `ark_seedance_shots` | **是** |
| 视频查询 | `volc-ark` | `ark_seedance_list` / `ark_seedance_get` / `ark_seedance_wait` | 否 |
| 视频下载 | `volc-ark` | `ark_seedance_download` | 否 |
| 任务归档 | `volc-ark` | `ark_list_tasks` | 否 |

### CLI 直接调用（MCP 不可用时等价）

MCP 工具本质是 Python CLI 的薄包装。MCP 未启动时，通过 Bash 直接调用：

| 操作 | CLI 命令 |
|------|----------|
| 提交 segments | `python3 mcps/volc-ark/scripts/ark_seedance_video.py segments EP01 --project-root dramas/<剧名>` |
| 提交 shots | `python3 mcps/volc-ark/scripts/ark_seedance_video.py shots EP01 --project-root dramas/<剧名>` |
| 查询任务 | `python3 mcps/volc-ark/scripts/ark_seedance_video.py get --task-id cgt-xxx` |
| 列出远程任务 | `python3 mcps/volc-ark/scripts/ark_seedance_video.py list --json` |
| 下载视频 | `python3 mcps/volc-ark/scripts/ark_seedance_video.py download --task-id cgt-xxx -o out.mp4` |
| 生成图片（当前默认引擎 gpt-image；CLI 路径随引擎，见 `mcps/shared/engine_registry.py`） | `python3 mcps/gpt-image/scripts/gpt_image.py generate --prompt "..." --output path.png` |

**环境变量**：`export ARK_API_KEY=xxx`（或 `DRAMA_PROJECT_ROOT=dramas/<剧名>`）

**⚠️ 严禁创建临时提交脚本** — 所有提交必须通过上述 CLI，其内置归档和去重保护。

**自动化脚本**：
- `script/pipeline_episode.py` — 单集流水线自动化
- `script/local_pipeline.py` — 本地拼接流水线
- `script/tts_batch_edge.py` — edge-tts 批量配音
- `script/gen_srt_from_clips.py` — 字幕生成
- `script/mix_tts_from_srt.py` — TTS 混音

## 竖屏规范

- **画面比例**：9:16（竖屏优先）
- **单集时长**：1-1.5 分钟（默认90秒；EP01可至2分钟）
- **每集镜头数**：16-30 个有效镜头（EP01 20-36；v2.2 切镜节奏，单镜理想 3-6s，基准：台词节奏基准.md §五）
- **总集数**：60-100 集（默认 86 集，standard-86）
- **总时长**：≥120 分钟（standard-86: 86×90s≈129 分钟，对齐平台 120 分钟精品档）

---

# 视频资产与安全规则

本仓库 `dramas/错嫁后我改写了王朝/素材/generated/` 用于存放**即梦等平台导出的正式分镜 MP4**，与 `script/config_ep01.json` / `script/ep01_clip_list.txt` 中的路径一一对应。

## 严禁事项

1. **禁止**向 `generated/` 写入**占位视频、测试条、纯色条**等与即梦导出**同名**的文件。覆盖写入会**不可恢复地毁掉**用户素材（回收站通常没有副本）。
2. **禁止**在未经用户明确同意时，用脚本批量**覆盖**该目录下已有 `.mp4`。
3. 自动化脚本、MCP、一次性实验：占位或测试输出必须写到 **`generated/_placeholders/`**（需自建），并使用**不同文件名**，不得占用 `第NN镜_*_jimeng.mp4` 命名。

## 运行流水线前检查

在仓库根执行：

```bash
ls -lh dramas/错嫁后我改写了王朝/素材/generated/*.mp4
```

- **正常即梦导出**：单文件多为**数 MB 级**（视分辨率与时长而定）。
- **异常**：单文件仅**数 KB** 多为占位/损坏，**不要**继续 `local_pipeline`，应先恢复真实素材。

## `.gitignore` 说明

`generated/` 通常被忽略，**Cursor / 部分搜索工具可能列不出其中文件**，不代表磁盘上为空。判断是否存在、体积多大**以终端 `ls` / `ffprobe` 为准**。

## 素材丢失后的挽回途径

- 即梦 / 控制台**任务历史**中重新下载。
- **Time Machine**或磁盘**本地快照**。
- 若仍有**已拼接成片**（如 `素材/output/` 下大体积 MP4），画面仍在，但**难以无损拆回**多段分镜，需重新导出分镜或手动按时间轴切分。

## 用 MCP 还能不能把即梦结果下回来？

**可以，路径有两条。**

### A. 方舟任务列表（最近约 7 天，无需事先记 task_id）

若走**火山方舟**等内容生成，可使用**`GET …/api/v3/contents/generations/tasks`**（API Explorer）。本仓库提供：

- 命令行：`python3 script/ark_generation_tasks.py list` / `download`（**`ARK_API_KEY`**，Bearer）。
- MCP（**`volc-jimeng`**）：**`ark_list_generation_tasks`**、**`ark_download_ark_videos`**（`mcp.json` 的 `env` 中配置 **`ARK_API_KEY`**）。
- MCP（**`volc-ark`**，推荐 Seedream/Seedance）：**`ark_seedance_list`**、**`ark_seedance_download`**、**`ark_list_tasks`**；本地归档 **`video/ark_tasks/`**。配置仅需 **`ARK_API_KEY`**，见 **`mcps/volc-ark/README.md`**。

列表约保留**7 天**；**`content.video_url` 约 24 小时有效**。**`download --ep01-names`**按**创建时间升序**取前 14 条成功任务并命名；若同期还有别的视频，镜序可能错位，请先**`list --json`**核对。

### B. 视觉智能 CVSync2AsyncGetResult（需 task_id）

**`volc_visual_query`**需**提交任务时返回的 `task_id`**，无法枚举全站历史。

在你仍持有每条 `task_id`（或能从控制台 / 笔记里查到）的前提下：

1. **`volc_visual_query`**：传入 `task_id`（及 `req_key`，常见 `jimeng_ti2v_v30_pro`），在返回 JSON 里取**视频直链**。
2. **`volc_download_video`**：传入直链，`filename` 与 `script/config_ep01.json` 一致（如 `第01镜_场1-1A_jimeng`），落到**`generated/`**（或 `VOLC_DOWNLOAD_DIR`）。

若没有**`task_id`**：**视觉查询**走不通时，可试**方舟列表**（A），或**网页历史下载**/**重新生成**。

**建议**：以后每镜生成成功时，顺手把**`task_id` + 镜号文件名**记在 `script/` 下一份自己的表格或 md 里，本地文件丢了还能用 MCP 按 ID 再拉一次。

**批量下回本地（推荐）**：复制 `script/ep01_task_ids.example.json` 为**`script/ep01_task_ids.json`**，在即梦创作记录里把 14 条**`task_id`**粘进去，仓库根执行：

```bash
export VOLC_ACCESS_KEY=… VOLC_SECRET_KEY=…
python3 script/download_jimeng_from_tasks.py
```

可先 `--dry-run` 只看接口返回是否含视频地址。脚本会写入**`generated/`**，文件名与 `script/config_ep01.json` 一致。`ep01_task_ids.json` 已加入 `.gitignore`。

## 与脚本的关系

- `gen_srt_from_clips.py`、`local_pipeline.py` **只读取** `generated/` 中配置路径；**不得**被修改为向该目录写入占位内容。
- 若需「空跑验证」，使用**`--dry-run`**（若脚本支持）或单独测试目录。

## 代码修改与提交规则

1. **不要自动提交**：每次修改代码后，等待用户明确要求再提交。
2. **批量提交**：多个相关改动合并为一次提交。
3. **提交前确认**：询问用户提交信息是否正确。

## volc-ark MCP（方舟 Seedream / Seedance）

与 **`volc-jimeng`**（视觉 AK/SK）并列的独立 MCP：**`mcps/volc-ark/`**，Cursor 配置名 **`volc-ark`**，**`env` 仅需 `ARK_API_KEY`**（示例见 **`.cursor/mcp.json.example`**）。

| 工具                                      | 扣费   | 说明                                                             |
| ----------------------------------------- | ------ | ---------------------------------------------------------------- |
| `ark_seedream_docs` / `ark_seedance_docs` | 否     | 文档                                                             |
| `ark_list_tasks`                          | 否     | 读 **`video/ark_tasks/`**                                        |
| `ark_seedance_list` / `get` / `wait`      | 否\*   | 查询/轮询已有任务（\*wait 不新建任务）                           |
| `ark_seedance_download`                   | 否     | 下载成片；路径须用户指定，勿覆盖 **`video/generated/`** 正式分镜 |
| `ark_seedream_generate` / `batch`         | **是** | Seedream 5.0 lite                                                |
| `ark_seedance_create` / `shots`           | **是** | Seedance 2.0 fast；本地图 **data URI**，无需图床                 |

短剧素材输出：**`dramas/<剧名>/assets/generated/`**（如天工开物），与错嫁 **`video/generated/`** 分开。

## 🚫 禁止调用视频/图片生成 MCP 工具

**除非用户明确要求，否则严禁调用以下 MCP 工具：**

- `jimeng_image_submit`（即梦图片生成）
- `volc_visual_submit`（通用视觉提交，可用于 jimeng/kling 视频和图片）
- `volc_visual_query`（查询视觉任务状态）
- `kling_image_*`、`kling_video_*`（Kling 相关）
- `minimax_text_to_image`（MiniMax 图片生成）
- **`gpt_image_generate`、`gpt_image_batch`**（gpt-image 出图）
- **`ark_seedream_generate`、`ark_seedream_batch`**（方舟 Seedream 出图）
- **`ark_seedance_create`、`ark_seedance_shots`**（方舟 Seedance 出视频）

**违规调用将浪费用户金钱！调用前必须获得用户明确授权！**

## 视频生成规则

1. **尽量带素材**：使用 `ark_seedance_create` / `ark_seedance_shots` 时，优先传入相关角色/场景参考图，确保一致性。
2. **竖屏优先**：默认使用 9:16 竖屏比例。
3. **质量优先**：使用 Seedance 2.0 fast 模型生成。

## AI素材生成流程

生成 AI 素材前，必须先读取以下文档：

1. 对应剧本的 `资产/角色卡片.md` — 获取角色 Prompt
2. 对应剧本的 `资产/场景卡片.md` — 获取场景 Prompt
3. 对应剧本的 `制片规范.md` — 了解 ID 系统和分段规则

然后基于文档中的规则和 Prompt 生成素材，不要凭空编造规则。

## 制作资质：其他微短剧

当前资质为**「其他微短剧」**（总投资 < 30万元，一般题材），由平台负责内容审核，定期报属地省级广电主管部门备案。

> **NRTA 分级标准（2026年7月最新）**：
> - 重点微短剧：≥80万元 或特殊题材 → 广电总局统一备案公示
> - 普通微短剧：30万元(含) ~ 80万元 → 省级广电备案+成片审查
> - 其他微短剧：< 30万元 → 平台自审 + 属地备案
>
> 注：此前旧版为 100万/30-100万/<30万，已于2026年7月调整。详见 `docs/动画微短剧_漫剧_内容创作建议.md`

### 题材硬约束

**禁止触碰以下特殊题材**（需广电总局或省级备案的剧本不可选）：

- **政治**：现代政治体制、时政议题、党政题材（注意：古代宫廷权谋/皇位争夺**不属于**政治题材，同《甄嬛传》走普通备案）
- **军事**：军旅征战、将军成长、女扮男装从军
- **司法/公安**：刑侦破案、警察主角、律师法庭、监狱出狱
- **国家安全/外交/统战/民族/宗教**：涉敏内容
- **封建迷信**：宣扬迷信思想（注意：神话/玄幻作为世界观背景且核心导向非迷信，可做）

### 剧本题材风险分级

> **核心原则**：判断依据是**故事核心导向**，而非"是否出现某个元素"。
> 同一个设定（如宫廷/鬼怪/法庭），如果核心是爱情/冒险/推理，且不宣扬不良价值观，可以做。

#### 🔴 A级：明确不可做（核心剧情直接涉及特殊题材）

| 剧本             | 原因                                     |
| ---------------- | ---------------------------------------- |
| 《超雄重生1995》 | 核心剧情是**刑侦破案**，主角身份是警察   |
| 《制式离婚》     | 核心剧情围绕**法庭诉讼**展开             |
| 《大宋提硒土》   | 核心背景是**王安石变法**，政治斗争为主线 |
| 《大秦第一功》   | 核心涉及**军事征战+朝堂政治**            |
| 《收骨册》       | 核心剧情是**古代验尸查案**，司法为主线   |
| 《第七个证人》   | 核心剧情围绕**法庭/书记员**展开          |
| 《读唇》         | 核心剧情是**法庭审判**                   |
| 《出狱48小时》   | 核心设定是**出狱/监狱**                  |
| 《上午她记得》   | 核心剧情是**法律诉讼**                   |

#### 🟡 B级：需逐本评估（有特殊元素但可通过改写规避）

**宫廷/权谋类** — 古代宫廷/权谋**不属于"政治"题材**（政治指现代政治体制/时政），同《甄嬛传》《延禧攻略》走普通备案。可做：

| 剧本                   | 说明                                      |
| ---------------------- | ----------------------------------------- |
| 《凤谋》               | 古装宫廷权谋，普通备案可做                |
| 《错嫁后我改写了王朝》 | 古装宫廷权谋，已在制作中                  |
| 《将门孤女》           | 古装+军旅，⚠️ 军旅元素需评估（将军/征战） |
| 《穿越布衣》           | 古装穿越权谋                              |
| 《赐死前夜》           | 古装宫廷+时间回滚                         |
| 《皇子他重生了》       | 古装宫廷重生                              |
| 《我在皇宫卖保险》     | 古装喜剧，宫廷仅为背景                    |
| 《我观音婢女》         | 古装宫廷                                  |
| 《布衣账房》           | 古装权谋                                  |
| 《九八送报夜》         | 年代市井群像，需确认无涉政敏感事件        |

> ⚠️ **注意**：宫廷剧虽不算"政治"，但仍有其他红线：
>
> - 不得影射/隐喻现实政治（如暗讽当朝）
> - 不得美化宫廷暴力/权斗中的极端手段
> - 军旅/征战元素（如《将门孤女》）仍属"军事"题材，需单独评估

**神话/玄幻类** — 如果核心是**冒险/喜剧/破除迷信**而非宣扬迷信，可做：

| 剧本                   | 可能的调整方向                                  |
| ---------------------- | ----------------------------------------------- |
| 《聊斋世界大冒险》     | 核心是**冒险/探案/喜剧**，鬼怪仅作世界观背景    |
| 《封神榜之我成了纣王》 | 经典文学IP改编，核心是**穿越/改命/爽文**        |
| 《西游路上开副本》     | 经典文学IP改编，核心是**冒险/喜剧**             |
| 《神仙转世》           | 如果核心导向是**破除迷信/成长**，可规避         |
| 《天庭临时工》         | 如果走**反讽/喜剧/破除迷信**路线，可规避        |
| 《食神》               | 需确认核心是美食还是神话/宗教                   |
| 《大禹治水》           | 经典神话IP，核心是**理工穿越/治水**，非宣扬迷信 |

#### 🟢 C级：可以做（一般题材）

| 剧本                         | 类型            | 说明                                            |
| ---------------------------- | --------------- | ----------------------------------------------- |
| 《她的克隆》                 | 科幻/情感       | 一般题材，场景少，成本可控                      |
| 《烬余》                     | 古装悬疑（6集） | 聚焦破案推理，无政治/军事主线                   |
| 《全楼都觉得我和女明星同居》 | 都市轻喜        | 纯都市恋爱，场景简单                            |
| 《都市债神》                 | 都市/神话       | 神话元素需确保"破除迷信"导向                    |
| 《天工开物之匠魂》           | 古装/理工       | ⚠️ 明末+阉党博弈，需弱化政治线，强化技术/爱情线 |
| 《我哥搞装修》               | 都市/轻喜       | 场景少，纯生活流                                |
| 《早点见》                   | 都市/家庭       | 纯生活流                                        |
| 《快递站下午见》             | 都市/群像       | 纯生活流                                        |
| 《教练别加练了》             | 都市/职场       | 纯生活流                                        |
| 《全公司都以为我很有背景》   | 都市/轻喜       | 纯都市职场                                      |
| 《我租的女友真把我当老公了》 | 都市/恋爱       | 纯都市恋爱                                      |
| 《离婚后，他的系统漏气了》   | 都市/系统       | 纯都市设定                                      |
| 《拆迁这一家》               | 家庭/伦理       | 纯家庭伦理                                      |
| 《我在末世开早点摊》         | 末世/经营       | 架空设定，无政治元素                            |
| 《冥牌调解处》               | 都市/悬疑       | 神话元素需确保"破除迷信"导向                    |

### 内容级合规检查（Content-Level Compliance）

题材分级（A/B/C）仅在项目启动时判定**能否开工**。但即使是🟢C级题材，写作过程中仍可能产生不合规内容（不当台词、不健康关系描写、暴力过度等）。因此流水线实施**两层合规**：

| 层级 | 检查时机 | 执行者 | 作用 |
|------|----------|--------|------|
| **题材分级**（现有） | 项目初始化 | drama-director | 决定能否开工 |
| **内容合规**（新增） | 每集剧本完成时 | scene-writer 自检 + script-reviewer R2 | 决定能否过审 |

**内容级合规要点**：
- scene-writer 完成每集后必须执行自检清单第 19-23 项（红线/价值观/灰区/台词/题材特定）
- drama-director 在 G4 门控中验证合规自检通过后方可提交 R2
- script-reviewer R2 审核时以强化后的维度 4（P0-P3 分层清单）进行结构化合规评审
- P0 红线命中 → 维度 4 直接 1 分，硬门控不可放行

**参考文档**：`docs/references/platform-review-gate.md`（完整平台审查门控清单）

### 合规审查流程

1. **选题阶段**（题材级）：对照分级表，🔴A级直接排除，🟡B级进入改写评估，🟢C级直接推进
2. **B级剧本改写评估**：需逐集审查，确认核心导向不触及政治/军事/司法/迷信红线
3. **写作阶段**（内容级）：scene-writer 每集完稿后执行自检清单（第 19-23 项），G4 门控验证通过后方可提交审核
4. **审核阶段**（内容级）：script-reviewer R2 以维度 4 P0-P3 分层清单进行结构化合规评审
5. **内容合规**：同步参照巨量引擎《动画微短剧内容创作建议》（`docs/动画微短剧_漫剧_内容创作建议.md`）
6. **边界判断**：如仍无法判断，提交平台预审确认后再投入制作

---

_建议：在 Cursor 中已配置 `.cursor/rules/video-generated-safety.mdc`，与本文一致，便于 Agent 始终遵守。_
