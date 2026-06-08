# AI短剧制作标准流程

> 版本：v2.0
> 更新日期：2026年6月
> 适用范围：本仓库所有短剧项目（Agent 驱动 + MCP 工具链）

---

## 一、流程总览

本仓库采用 **Agent 流水线** 模式制作 AI 短剧，由 `drama-director`（总导演）统一调度 6 个专业 Agent 完成从故事概念到可提交 API 的 YAML 输出。

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      AI短剧 Agent 流水线（6 阶段）                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Stage 1          Stage 2          Stage 3a/3b        Stage 4   Stage 5  │
│  story-architect  production-      character-designer  scene-    segment- │
│  故事架构师        planner          角色设计师(并行)    writer    builder  │
│                   制片结构注册师    scene-prop-designer 分镜编剧  分镜构建 │
│                                    场景道具设计师(并行)                    │
│                                                                          │
│  [G1] ─────────── [G2] ─────────── [G3] ────────────── [G4] ──── [G5]   │
│        R1 审查                                           R2 审查          │
└──────────────────────────────────────────────────────────────────────────┘
```

| 阶段 | Agent | 核心产出 |
|------|-------|----------|
| Stage 1：故事架构 | `story-architect` | `短剧剧本_<剧名>_36集.md`（36集大纲） |
| Stage 2：制片规范 | `production-planner` | `制片规范.md` + `资产/` 骨架卡（ID 系统） |
| Stage 3a：角色设计 | `character-designer` | `资产/角色卡.md` + `assets/looks/` 形象图 |
| Stage 3b：场景道具 | `scene-prop-designer` | `资产/场景卡.md` + `assets/scenes/` 参考图 |
| Stage 4：分镜编剧 | `scene-writer` | `剧本/EP##/EP##_*.md`（分集剧本 + 镜头表） |
| Stage 5：分镜构建 | `segment-builder` | `EP##_shots.yaml` + `EP##_segments.yaml` |

**辅助角色**：
- `script-reviewer`（剧本审核师）：R1（大纲后）/ R2（EP01 剧本后）质量门控
- `drama-director`（总导演）：流水线调度、门控判定

---

## 二、Stage 1：故事架构

**执行者**：`story-architect`（故事架构师）

**输入**：剧本概念（标题 + 类型 + 核心钩子 + 目标受众）

**产出**：
- `短剧剧本_<剧名>_36集.md` — 36 集完整大纲
- 包含：情绪弧线、钩子矩阵、付费节点、集与集悬念结构

**规格**：
- 36 集 × 2.5-3 分钟/集
- 每集 8-14 个镜头
- 竖屏 9:16 格式

**门控 G1 → R1 审查**：`script-reviewer` 评分 ≥15/25 放行

---

## 三、Stage 2：制片规范

**执行者**：`production-planner`（制片结构注册师）

**输入**：36 集大纲

**产出**：
- `制片规范.md` — 项目"宪法"（ID 系统、分段规则、结构约束）
- `资产/角色卡.md` — CHAR-### 骨架卡（ID + 姓名 + 定位）
- `资产/场景卡.md` — SCENE-### 骨架卡
- `资产/道具卡.md` — PROP-### 骨架卡
- `资产/声音卡.md` — 音色分配

**ID 格式**：
| 类型 | 格式 | 示例 |
|------|------|------|
| 镜头 | `EP##-S##` | `EP01-S03` |
| 角色 | `CHAR-###` | `CHAR-001` |
| 场景 | `SCENE-###` | `SCENE-005` |
| 道具 | `PROP-###` | `PROP-012` |

**门控 G2**：制片规范完整、ID 系统无冲突

---

## 四、Stage 3：视觉资产设计（并行）

### 4.1 角色设计（Stage 3a）

**执行者**：`character-designer`（角色设计师）

**输入**：骨架卡 + 36 集大纲

**产出**：
- 完整 `资产/角色卡.md`（视觉描述 + AI Prompt + voice_prompt）
- `资产/形象索引.md`（形象图链接汇总）
- `assets/looks/` — Seedream 生成的角色参考图

**工具链**：
1. 编写英文 Seedream Prompt
2. 调用 `ark_seedream_generate`（需用户授权）生成形象图
3. 调用 `imgbb_upload` 托管图片获取 URL
4. 迭代至质量达标

### 4.2 场景道具设计（Stage 3b）

**执行者**：`scene-prop-designer`（场景道具设计师）

**输入**：骨架卡 + 36 集大纲

**产出**：
- 完整 `资产/场景卡.md`（视觉描述 + AI Prompt）
- 完整 `资产/道具卡.md`
- `assets/scenes/` — 场景参考图

**工具链**：同角色设计（Seedream + imgbb）

**门控 G3**：角色/场景形象图就绪，可供下游引用

---

## 五、Stage 4：分镜编剧

**执行者**：`scene-writer`（分镜编剧）

**输入**：36 集大纲 + 制片规范 + 角色卡 + 场景卡

**产出**：`剧本/EP##/EP##_分集剧本.md` — 含 11 列镜头表

**镜头表格式**：

| 镜号 | Segment | 景别 | 画面描述 | 角色 | 对白/旁白 | 动作指令 | 镜头运动 | 音效 | 时长 | 备注 |
|------|---------|------|----------|------|-----------|----------|----------|------|------|------|

**关键规范**：
- 每集总台词 + 独白 + 旁白 ≥ 50 行
- 全集最多 1 个无台词 Segment
- 每集 2-3 句"可截图分享"金句
- 场景经济学：每场戏至少服务 2 个功能

**门控 G4 → R2 审查**：EP01 硬门控 ≥18/25，EP02+ 软门控 ≥15/25

---

## 六、Stage 5：分镜构建

**执行者**：`segment-builder`（分镜构建师）

**输入**：分集剧本 `.md` + 制片规范 + 资产参考图

**产出**：
1. `EP##_shots.yaml` — 逐镜头结构化描述（中间产物）
2. `EP##_segments.yaml` — 按 Segment 合并的 API 提交配置（最终产物）

**下游消费者**：
- `script/pipeline_episode.py` — 读取 YAML 自动提交 Seedance API
- `ark_seedance_shots` MCP 工具 — 直接消费 YAML 结构

**门控 G5**：YAML schema 校验通过

---

## 七、MCP 工具链

本项目通过 MCP（Model Context Protocol）调用外部 AI 生成服务。

### 7.1 图片生成（volc-ark / Seedream）

| 工具 | 用途 | 扣费 |
|------|------|------|
| `ark_seedream_generate` | 单张图片生成 | **是** |
| `ark_seedream_batch` | 批量图片生成 | **是** |
| `ark_seedream_docs` | 查看文档 | 否 |

**配置**：`ARK_API_KEY`（见 `.cursor/mcp.json.example`）

### 7.2 图片托管（imgbb）

| 工具 | 用途 | 扣费 |
|------|------|------|
| `imgbb_upload` | 上传图片获取公开 URL | 否 |

**用途**：角色/场景参考图上传后获取 URL，供 YAML 和文档引用。

### 7.3 视频生成（volc-ark / Seedance 2.0）

| 工具 | 用途 | 扣费 |
|------|------|------|
| `ark_seedance_create` | 单条视频生成 | **是** |
| `ark_seedance_shots` | 批量按 YAML 生成 | **是** |
| `ark_seedance_list` / `get` / `wait` | 查询/轮询任务 | 否 |
| `ark_seedance_download` | 下载生成结果 | 否 |
| `ark_seedance_docs` | 查看文档 | 否 |

**规范**：
- 默认 9:16 竖屏
- 使用 Seedance 2.0 fast 模型
- 尽量传入参考图（角色/场景），确保一致性

### 7.4 配音（edge-tts）

| 工具/脚本 | 用途 |
|-----------|------|
| `script/tts_batch_edge.py` | 批量 edge-tts 配音 |
| `script/mix_tts_from_srt.py` | TTS 混音到视频 |
| `script/gen_srt_from_clips.py` | 从剧本生成 SRT 字幕 |

### 7.5 视频拼接与后期

| 脚本 | 用途 |
|------|------|
| `script/pipeline_episode.py` | 单集流水线自动化（生成 → TTS → 拼接） |
| `script/local_pipeline.py` | 本地拼接流水线（读取 generated/ 中视频） |
| `script/split_video_segments.py` | 视频按时间轴切分 |

---

## 八、项目文件结构

每个短剧项目遵循统一目录规范：

```
dramas/<剧名>/
├── 资产/                      ← 结构化资产卡
│   ├── 角色卡.md             ← 角色视觉 + Prompt + voice_prompt
│   ├── 形象索引.md           ← 形象图 URL 汇总
│   ├── 场景卡.md             ← 场景视觉 + Prompt
│   ├── 道具卡.md             ← 道具视觉 + Prompt
│   └── 声音卡.md             ← 音色分配
├── 剧本/
│   └── EP01/                 ← 单集目录
│       ├── EP01_分集剧本.md  ← 分镜编剧产出
│       ├── EP01_shots.yaml   ← 逐镜头 YAML
│       └── EP01_segments.yaml ← API 提交 YAML
├── assets/                    ← AI 生成的媒体文件
│   ├── generated/            ← 视频素材（Seedance 输出）
│   ├── looks/                ← 角色形象图（Seedream 输出）
│   └── scenes/               ← 场景参考图
├── 制片规范.md               ← 项目宪法（ID 系统 + 分段规则）
├── 工作计划.md               ← 流水线状态追踪
└── 短剧剧本_<剧名>_36集.md  ← 36集大纲
```

---

## 九、安全规则

### 🚫 禁止调用生成 MCP 工具（除非用户明确授权）

以下工具**每次调用都会产生费用**，必须获得用户明确授权后才能调用：

- `ark_seedream_generate` / `ark_seedream_batch`（图片生成）
- `ark_seedance_create` / `ark_seedance_shots`（视频生成）
- `jimeng_image_submit`（即梦图片）
- `volc_visual_submit`（通用视觉提交）

### 🚫 禁止覆盖已有视频素材

- `generated/` 目录下的 `.mp4` 文件为正式分镜素材
- **禁止**写入占位视频、测试条、纯色条
- **禁止**未经用户同意批量覆盖
- 测试输出须写入 `generated/_placeholders/`

### 代码修改规则

1. **不要自动提交**：等待用户明确要求
2. **批量提交**：相关改动合并为一次提交
3. **提交前确认**：询问用户提交信息

---

## 十、质量检查清单

### 每集发布前检查

- [ ] 视频比例正确（9:16 竖屏）
- [ ] 字幕时间轴准确
- [ ] 音量平衡（人声 > 音效 > BGM）
- [ ] 开头 3 秒有画面冲击
- [ ] 结尾有悬念/引导关注
- [ ] 无平台违禁词/画面
- [ ] 角色形象一致性（跨镜头检查）

### 版权检查

- [ ] BGM 有商用授权
- [ ] 参考素材已原创化
- [ ] 无品牌 LOGO 入镜

---

## 十一、平台发布规范

| 平台 | 视频比例 | 最佳时长 | 特点 |
|------|----------|----------|------|
| 抖音 | 9:16（竖屏） | 1-3 分钟/集 | 流量大、算法强 |
| 快手 | 9:16（竖屏） | 1-3 分钟/集 | 社区强 |
| 视频号 | 16:9 或 9:16 | 1-3 分钟/集 | 微信生态 |

---

## 文档更新记录

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-04-04 | 初始版本，基于《天庭临时工》剧本创建 |
| v2.0 | 2026-06-08 | 全面重写：Agent 流水线架构、MCP 工具链、统一项目结构 |
