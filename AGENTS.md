# AI 短剧制作流水线

本仓库采用 Agent 驱动的 6 阶段制作流水线，由 `drama-director`（总导演）统一调度。

> **[Copilot] Agent 规范已同步至 VS Code Copilot 的 `/memories/repo/`**，Copilot 对话时自动加载上下文（其他工具不会读取此路径）。详见：
> - `pipeline.md` — 流水线阶段、门控、并行规则
> - `agent-specs.md` — 各 Agent 核心规范速查
> - `id-format.md` — ID 格式、命名规范、项目结构
> - `output-templates.md` — 关键输出格式与模板
> - `safety-rules.md` — 安全禁止规则、题材约束
> 
> 完整 Agent 定义文件位于 `.qoder/agents/` 目录（Qoder/Cline 专用，Copilot 通过 `/memories/repo/` 读取）。

## 流水线阶段

```
概念 → [Stage 1] → G1 → [Stage 2] → G2 → ┌─[Stage 3a]─┐ → G3 → [Stage 4] → G4 → [Stage 5] → G5
         故事架构          制片规范         │  角色设计   │        分镜编剧         分镜构建
                                           └─[Stage 3b]─┘
                                              场景道具设计
```

| Stage | Agent | 职责 | 核心产出 |
|-------|-------|------|----------|
| 1 | `story-architect`（故事架构师） | 36集故事大纲、情绪弧线、钩子矩阵 | `短剧剧本_<剧名>_36集.md` |
| 2 | `production-planner`（制片结构注册师） | ID 系统、资产骨架、分段规则 | `制片规范.md` + `资产/` 骨架卡 |
| 3a | `character-designer`（角色设计师） | 角色视觉设计、形象图生成 | `资产/角色卡片.md` + `assets/looks/` |
| 3b | `scene-prop-designer`（场景道具设计师） | 场景/道具视觉设计、参考图 | `资产/场景卡片.md` + `assets/scenes/` |
| 4 | `scene-writer`（分镜编剧） | 分集剧本、镜头表 | `剧本/EP##/EP##_*.md` |
| 5 | `segment-builder`（分镜构建师） | YAML 生成供 API 提交 | `剧本/EP##/EP##_shots.yaml` + `EP##_segments.yaml` |

**辅助角色**：
- `script-reviewer`（剧本审核师）：R1（大纲后）和 R2（EP01 剧本后）质量门控
- `drama-director`（总导演）：流水线调度、门控判定、状态追踪

## 质量门控（Gate）

| 门控 | 位置 | 职责 |
|------|------|------|
| G1 | Stage 1 → Stage 2 | 大纲完整性校验 |
| G2 | Stage 2 → Stage 3 | 制片规范 + ID 系统就绪 |
| G3 | Stage 3 → Stage 4 | 角色/场景资产就绪 |
| G4 | Stage 4 → Stage 5 | 分集剧本定稿 |
| G5 | Stage 5 完成 | YAML 合规校验 |

**审查节点**：
- **R1**（G1 之后）：`script-reviewer` 审查 36 集大纲，≥15/25 分放行
- **R2**（G4 之后）：`script-reviewer` 审查单集剧本，EP01 ≥18/25 硬门控
- **R2 视觉资产模式**：当 Stage 3a/3b 视觉资产可用时，满分调整为 30 分（新增"视觉资产匹配度"维度），EP01 硬门槛调整为 ≥22/30

## ID 格式

- **镜头 ID**：`EP##-S##`（两段式：集号-镜号）
- **角色 ID**：`CHAR-###`
- **场景 ID**：`SCENE-###`
- **道具 ID**：`PROP-###`

## 项目文件结构

```
dramas/<剧名>/
├── 资产/              ← 角色卡片.md, 形象索引.md, 场景卡片.md, 道具卡片.md, 声音卡片.md
├── 剧本/EP01/         ← 分集剧本 + 分镜脚本 + YAML
├── assets/            ← AI 生成素材
│   ├── generated/     ← 视频素材（Seedance 输出）
│   ├── looks/         ← 角色形象参考图（Seedream 输出）
│   └── scenes/        ← 场景参考图
├── 制片规范.md        ← 项目"宪法"（ID 系统、分段规则）
├── 工作计划.md        ← 流水线状态追踪
└── 短剧剧本_<剧名>_36集.md  ← 36集大纲
```

## MCP 工具链

| 功能 | MCP 服务 | 工具 | 扣费 |
|------|----------|------|------|
| 图片生成 | `volc-ark` | `ark_seedream_generate` / `ark_seedream_batch` | **是** |
| 图片托管 | `imgbb` | `imgbb_upload` | 否 |
| 视频生成 | `volc-ark` | `ark_seedance_create` / `ark_seedance_shots` | **是** |
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
| 生成图片 | `python3 mcps/volc-ark/scripts/ark_seedream_image.py generate --prompt "..." --output path.png` |

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
- **单集时长**：2.5-3 分钟
- **每集镜头数**：15-30 个镜头

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

当前资质为**「其他微短剧」**（总投资 < 100万元，一般题材），由平台负责内容审核，定期报属地省级广电主管部门备案。

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

### 合规审查流程

1. **选题阶段**：对照分级表，🔴A级直接排除，🟡B级进入改写评估，🟢C级直接推进
2. **B级剧本改写评估**：需逐集审查，确认核心导向不触及政治/军事/司法/迷信红线
3. **内容合规**：同步参照巨量引擎《动画微短剧内容创作建议》（`docs/动画微短剧_漫剧_内容创作建议.md`）
4. **边界判断**：如仍无法判断，提交平台预审确认后再投入制作

---

_建议：在 Cursor 中已配置 `.cursor/rules/video-generated-safety.mdc`，与本文一致，便于 Agent 始终遵守。_
