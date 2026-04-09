# 视频资产与安全规则

本仓库 `短剧/错嫁后我改写了王朝/素材/generated/` 用于存放**即梦等平台导出的正式分镜 MP4**，与 `script/config_ep01.json` / `script/ep01_clip_list.txt` 中的路径一一对应。

## 严禁事项

1. **禁止**向 `generated/` 写入**占位视频、测试条、纯色条**等与即梦导出**同名**的文件。覆盖写入会**不可恢复地毁掉**用户素材（回收站通常没有副本）。
2. **禁止**在未经用户明确同意时，用脚本批量**覆盖**该目录下已有 `.mp4`。
3. 自动化脚本、MCP、一次性实验：占位或测试输出必须写到 **`generated/_placeholders/`**（需自建），并使用**不同文件名**，不得占用 `第NN镜_*_jimeng.mp4` 命名。

## 运行流水线前检查

在仓库根执行：

```bash
ls -lh 短剧/错嫁后我改写了王朝/素材/generated/*.mp4
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
- MCP：**`ark_list_generation_tasks`**、**`ark_download_ark_videos`**（`mcp.json` 的 `env` 中配置**`ARK_API_KEY`**）。

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

## 🚫 禁止调用视频/图片生成MCP工具

**除非用户明确要求，否则严禁调用以下MCP工具：**

- `jimeng_image_submit`（即梦图片生成）
- `volc_visual_submit`（通用视觉提交，可用于jimeng/kling视频和图片）
- `kling_image_*`、`kling_video_*`（Kling相关工具）
- `minimax_text_to_image`（MiniMax图片生成）

**违规调用将浪费用户金钱！调用前必须获得用户明确授权！**

## 视频生成规则

1. **尽量带素材**：使用 `kling_image_to_video` 时，优先传入相关素材图片（用 `image_paths` 多图参数最多4张），确保角色/场景一致性。
2. **竖屏优先**：默认使用 9:16 竖屏比例。
3. **质量优先**：使用 `kling-v3-omni` 模型生成。

## AI素材生成流程

生成 AI 素材前，必须先读取以下文档：

1. `短剧/天庭临时工/AI素材清单_1-3集.md` - 了解生成规范
2. `短剧/天庭临时工/角色卡.md` - 获取角色 Prompt

然后基于文档中的规则和 Prompt 生成素材，不要凭空编造规则。

## MiniMax MCP 使用规则

**MiniMax MCP** (`project-0-demo1-minimax`) 支持文生图、文生音频等功能：

### 文生图 (`minimax_text_to_image`)

- **默认比例**：9:16 竖屏（与视频一致）
- **模型**：`image-01`
- **输出目录**：`短剧/天庭临时工/素材/`（按角色归类）
- **Prompt 优化**：建议关闭 `prompt_optimizer: false`，使用角色卡中已有的英文 Prompt

---

_建议：在 Cursor 中已配置 `.cursor/rules/video-generated-safety.mdc`，与本文一致，便于 Agent 始终遵守。_
