# Seedance 2.0 分镜格式与 API 映射

> **目标**：分镜 → `shots.yaml` → 火山方舟 **异步任务** `POST …/contents/generations/tasks`；生成前**先备齐参考图/首帧图**（本地路径即可，**无需图床**，提交时转 data URI）。  
> **模型（中国区示例）**：`doubao-seedance-2-0-fast-260128`（快，**默认**）/ `doubao-seedance-2-0-260128`（标准）  
> **Base URL**：`https://ark.cn-beijing.volces.com/api/v3`

## 官方文档（你提供的教程入口）

| 文档 | 链接 | 用途 |
|------|------|------|
| **Doubao Seedance 2.0 系列教程（SDK 示例）** | [2291680](https://www.volcengine.com/docs/82379/2291680?lang=zh) | 调用方式、多模态入参示例 |
| Seedance 2.0 提示词指南 | [2222480](https://www.volcengine.com/docs/82379/2222480?lang=zh) | 主体/风格/运镜/规格五要素 |
| Seedream 4.0 助力 Seedance 最佳实践 | [1951250](https://www.volcengine.com/docs/82379/1951250?lang=zh) | **用 Seedream 出分镜关键帧 → 再喂 Seedance** |
| API 参考 | [1393047](https://www.volcengine.com/docs/82379/1393047?lang=zh) | 字段说明 |
| 输出格式 / 裁剪规则 | [1366799](https://www.volcengine.com/docs/82379/1366799?lang=zh) | 分辨率、ratio、图片约束 |

> 控制台页面为 JS 渲染，本地以 **SDK 教程 + API 参考** 为准；接入以你账号下控制台显示的 **model id** 为最终值。

---

## 一、整体流水线

```
角色卡/场景卡 (CHAR/SCENE)
    ↓ ① 定妆图
assets/looks/*.png          assets/scenes/*.png
    ↓ ② 合首帧（可选：场景底图 + 人物融图）
assets/keyframes/EP01/EP01-S02_first.png
    ↓ ③ 分镜 shots JSON/YAML
    ↓ ④ API 批量提交
assets/generated/EP01/EP01-S02.mp4
    ↓ ⑤ 剪映：对白 TTS + 字幕（Seedance 不负责口型）
成片
```

**原则**：Seedance **一次任务 = 一条镜头（通常 4–8 秒）**；对白不在 API 里生成，用后期轨。

---

## 二、API 真实形态（见 [系列教程 2291680](https://www.volcengine.com/docs/82379/2291680?lang=zh)）

Seedance 2.0 使用 **`content[]` 多模态数组** + 异步任务，不是旧式单一 `img_url` 字段。

```http
POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
```

要点：

- **`content`**：`text` + 多张 `image_url`（带 `role`）+ 可选 `video_url` / `audio_url`
- **`role`**：`first_frame` | `last_frame` | `reference_image` | `reference_video` | `reference_audio`
- **参考上限**：图 ≤9、视频 ≤3、音频 ≤3；提示词用 **`[图1][图2]`** 对应顺序
- **轮询**：`GET …/tasks/{id}` → `succeeded` → `content.video_url`（**24h 内转存**）
- **模型 id**：以控制台为准，默认 `doubao-seedance-2-0-fast-260128`

短剧推荐 `mode`：`i2v`（单关键帧）| `i2v_ref`（定妆+场景+首帧，一致性最好）| `t2v` | `skip`。  
关键帧可用 **Seedream 4.0** 生成后再进 Seedance（[1951250](https://www.volcengine.com/docs/82379/1951250?lang=zh)）。

完整 JSON 示例见本文 **§4.2** 与 [提示词指南 2222480](https://www.volcengine.com/docs/82379/2222480?lang=zh)。

---

## 三、现有分镜 vs API 缺口

当前 `分集剧本/EP01_*.md` 表格列：

| 已有列 | API / 资产 | 缺口 |
|--------|------------|------|
| 镜号 | `shot_id` | 需稳定 ID：`EP01-S02` |
| 场景 `SCENE-*` | 背景 Prompt / 场景图 | 需 `assets/scenes/` |
| 形象 `CHAR-*-L##` | 首帧人物 | 需 `assets/looks/` 定妆 |
| 景别 | 写入 `prompt` | 需映射表（特写→镜头特写） |
| 画面 | `prompt` 主体 | ✓ |
| 对白/备注 | **不进 API** | → `dialogue` + 剪映 SRT |
| — | `seconds` | **缺**：每镜时长 |
| — | `mode` | **缺**：文生/图生/跳过 |
| — | `first_frame` 路径 | **缺**：素材文件路径 |
| — | `seed` / `ratio` | **缺**：集级默认 + 镜级覆盖 |

---

## 四、推荐：双层结构

### 4.1 人类可读（继续用 Markdown）

保留 `分集剧本/EP##_*.md`，**增加列**：

| 镜号 | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 画面 | 运镜 | 对白/备注 |
|------|------|------|------|------|------|------|------|------|-----------|

**模式**枚举：

| 值 | 含义 |
|----|------|
| `skip` | 黑屏/字卡：不调用 API，剪映处理 |
| `t2v` | 文生视频（仅 `content.text`） |
| `i2v` | 首帧图 + 文本（**默认**） |
| `i2v_ref` | 定妆/场景 `reference_image` + 首帧（**一致性推荐**） |
| `i2v_ff` | 首尾帧 `first_frame` + `last_frame` |

### 4.2 机器可读（API 与素材清单）

每集一个文件：`分集剧本/EP01_shots.yaml`（或 `configs/EP01_seedance.json`）

```yaml
episode_id: EP01
defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast-260128
  ratio: "9:16"
  resolution: 720p
  duration: 5
  generate_audio: false
  watermark: false
  prompt_suffix: "明代苏州，天启年间，古风写实，电影感竖屏，无现代物品，无清晰汉字"

shots:
  - shot_id: EP01-S01
    shot_no: 1
    mode: skip

  - shot_id: EP01-S02
    shot_no: 2
    mode: i2v_ref          # 或 i2v（仅首帧图）
    duration_sec: 4
    refs:
      scene_id: SCENE-001
      look_ids: [CHAR-001-L01]
    assets:
      look_urls:
        CHAR-001-L01: assets/looks/CHAR-001-L01.png
      scene_urls:
        SCENE-001: assets/scenes/SCENE-001.png
      first_frame: assets/keyframes/EP01/EP01-S02_first.png
    api:
      # 脚本展开为 content[] + 顶层 duration/ratio/...
      text: "【图1】男主宋知行，【图2】卧室。镜头特写，猛然睁眼，瞳孔倒映木床，粗重呼吸。{{prompt_suffix}}"
      content_roles:
        - { file: CHAR-001-L01, role: reference_image }
        - { file: SCENE-001, role: reference_image }
        - { file: first_frame, role: first_frame }
      return_last_frame: true
      seed: 1001
    dialogue: []

  - shot_id: EP01-S05
    shot_no: 5
    mode: i2v
    duration_sec: 2
    assets:
      first_frame: assets/keyframes/EP01/EP01-S05_first.png
    api:
      text: "闪回0.5秒，现代手表敲键盘，叠化古代卧室"
      content_roles:
        - { file: first_frame, role: first_frame }
```

**脚本展开规则**（`script/storyboard_to_seedance.py` 已实现导出；API 提交待写）：

```bash
cd darams/天工开物 && python3 script/storyboard_to_seedance.py   # EP01–03
python3 script/storyboard_to_seedance.py EP04                    # 单集
```

产出：`分集剧本/EP##_shots.yaml`、`assets/keyframes/EP##/manifest.yaml`

| shots 字段 | 展开为 API |
|------------|------------|
| `api.text` | `content[]` 中 `{ type: text, text }` |
| `assets.*_urls` + `content_roles` | 上传 CDN 后 `{ type: image_url, image_url, role }` |
| `duration_sec` | `duration` |
| `defaults.*` | 请求体顶层字段 |
| `refs.look_ids` | 校验 looks 文件存在 |

**展开后的 JSON 片段示例（EP01-S02）**：

```json
{
  "model": "doubao-seedance-2-0-fast-260128",
  "content": [
    { "type": "text", "text": "【图1】男主……【图2】卧室。镜头特写……" },
    { "type": "image_url", "image_url": { "url": "…/CHAR-001-L01.png" }, "role": "reference_image" },
    { "type": "image_url", "image_url": { "url": "…/SCENE-001.png" }, "role": "reference_image" },
    { "type": "image_url", "image_url": { "url": "…/EP01-S02_first.png" }, "role": "first_frame" }
  ],
  "ratio": "9:16",
  "resolution": "720p",
  "duration": 4,
  "return_last_frame": true
}
```

---

## 五、素材图片清单（生成视频前必做）

### 5.1 第一层：定妆（已有 ID，缺文件）

| 目录 | 来源 ID | 文件示例 |
|------|---------|----------|
| `assets/looks/` | `CHAR-*-L01`（及 L02+） | `CHAR-001-L01.png` |
| `assets/scenes/` | `SCENE-*`（无人物） | `SCENE-001.png` |

规则：见 `角色卡.md` / `场景卡片.md` Prompt；**L02+ 必须基于 L01 图生图**。

### 5.2 第二层：镜头首帧（每镜一张，图生视频用）

| 目录 | 命名 | 合成方式 |
|------|------|----------|
| `assets/keyframes/EP01/` | `EP01-S{镜号}_first.png` | 场景图 + 人物定妆（融图/ControlNet/手动） |

**镜级 manifest**（便于检查「是否齐图」）：

```yaml
# assets/keyframes/EP01/manifest.yaml
required:
  - shot_id: EP01-S02
    first_frame: EP01-S02_first.png
    looks: [CHAR-001-L01]
    scene: SCENE-001
```

### 5.3 不必为每镜单独出「场景图」

- 同一场景多镜可**复用** `SCENE-001` 底图，只换人物 pose 的首帧合成。  
- `return_last_frame` 时，镜 N 的尾帧可另存为 `EP01-S{N}_last.png` 供 S{N+1} 作首帧。

---

## 六、Prompt 拼装规则（脚本实现）

从分镜行自动生成 `api.prompt`：

```
[运镜词] + [景别] + [画面列中文] + [时代/画幅后缀] + [negative 另字段]
```

| 景别 | 写入 Prompt |
|------|-------------|
| 特写 | 镜头特写 |
| 近景 | 镜头近景 |
| 中景 | 镜头中景 |
| 全景 | 镜头全景 |
| 主观 | 主观镜头 |
| 跟拍 | 镜头跟随 |
| 慢镜 | 慢动作 |
| 闪回 | 闪回、叠化 |

**集级后缀**（写进 `defaults.prompt_suffix`）：

> 明代苏州，天启年间，古风写实，电影感，竖屏9:16，无现代物品，无清晰汉字

**从 ID 解析**（不重复写脸）：

- 有 `first_frame` 图时，prompt **不写**五官细节，只写动作、光影、运镜。  
- 无图 `t2v` 时，拼接 `角色卡 L01` 简短外貌 + `场景卡片` 环境。

---

## 七、与仓库其他项目对齐

| 项目 | 可借鉴 |
|------|--------|
| `错嫁…/第01集_分镜与AI视频提示词.md` | 时长列、中英文 prompt、negative |
| `错嫁…/config_ep01.json` | 成片拼接顺序 `clips[]` |
| `即梦3.0Pro_Prompt与运镜备忘.md` | 运镜词表、对白后期 |
| `分集剧本/EP01` | CHAR/SCENE/形象 ID |

建议天工开物新增：

```
天工开物/
├── assets/
│   ├── looks/          # 定妆
│   ├── scenes/         # 空景
│   └── keyframes/EP01/ # 镜头首帧 + manifest.yaml
├── configs/
│   └── EP01_seedance.yaml   # shots + API
└── docs/
    └── Seedance2_分镜与API映射.md  # 本文件
```

---

## 八、EP01 体量估算（样片）

| 项目 | 数量 |
|------|------|
| 分镜行 | 26 |
| 需 API（非 skip） | 约 22（去掉黑屏/字幕 4 镜） |
| 定妆图 | looks 约 4 + scenes 约 3 = **7 张** |
| 首帧图 | 约 **22 张**（可部分用上一镜尾帧减少） |

---

## 九、下一步建议

1. **定稿** `EP01_shots.yaml` 结构（可先手工转 2–3 镜试 API）。  
2. **批量出** `assets/looks` + `assets/scenes`（禁止写入别剧 `generated/`）。  
3. ~~写 `storyboard_to_seedance.py`~~ → **`storyboard_submit_seedance.py`**：校验素材 → 展开 `POST` body → `configs/seedance_requests/`；`--submit` 写 `task_log.jsonl`。  
4. **`storyboard_keyframe_prompts.py`**：导出 `seedream_batch.yaml` + 每集 `seedream_prompts.yaml`（Seedream 出图用）。  
4. EP01 试跑 4 镜通过后，再扩 EP02–03。

---

## 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-05-19 | 草案；对齐现有 CHAR/SCENE 与 Seedance 2.0 参数 |
| v0.2 | 2026-05-19 | 按官方教程 2291680 修正为 content[]/contents/generations/tasks |
