# Kling 4.0 Flash 全面开放：官网+API+MCP/CLI/Adobe 插件；720p 无输入视频 $0.094/s

抓取时间：2026-11-05 08:40（Asia/Shanghai）  
层：国外  
过门：成本 / 产能（短剧制作模型价目与接入面）；非 Runway 渠道折扣、非 10-28 完整版 Kling 4.0 API

## 要点（只记可核事实）

- 官方 X @Kling_ai（2026-11-04 15:00 UTC，约北京 23:00）：**Kling 4.0 Flash Is Now Fully Available**——所有用户可在 Kling AI 官网与 **API** 使用；并可通过 **MCP、CLI、AI plugins**；Adobe **Photoshop / Premiere Pro / After Effects** 可灵插件可直接调。帖 impressions 约 **13.3k** / 194 likes / 27 reposts（2026-11-05 抓取）。
- 官方 API Updates（2026-11-04）：Flash API 上线；单条 **3–20 秒**、**720P**；路径 `/text-to-video/kling-4.0-flash`、`/image-to-video/kling-4.0-flash`、`/omni-video/kling-4.0-flash`；图生视频仅单首帧；Omni 单任务最多 **15** 输入；按总时长计费，细则见价目页。
- 官方 Video 价目页（已打开）：Flash **无输入视频** 720P = **0.6 Unit（$0.094）/s**；有输入视频单价行 **0.4 Unit（$0.063）/s**，但总时长在输入≤输出时按 **输出×2**、输入>输出时按 **输入+输出** 计——OrcaRouter 复算：10s 无输入 ≈ **$0.94**，10s←10s 输入 ≈ **$1.26**（输入视频行不是简单 33% 折扣）。Flash **无 1080p/4K 行、无原生音频行**。对照完整版 Kling 4.0 无输入 720P = **1.0 Unit（$0.157）/s**（Flash 标价约低 **40%**）。
- 背景（非本轮新事）：Flash 自 2026-09-28 起仅 Ultra Yearly（「黑金」年订）可用；完整版 Kling 4.0 API 已于 **10-28** 全量（最长 30s、720p/1080p）。本轮增量是 **Flash 全量开放 + 公开 API/插件面 + 价目可核**。
- 独立英文核验：TheReelStack（2026-11-04）复述官方开放面，并提醒公告未并列完整价目、切批量前查价目页；OrcaRouter（2026-11-04）逐行拆价目与 720p/20s 天花板。

## 对独立短剧制作方意味着什么

- **成本**：草稿/预演/空镜可优先压到 Flash **$0.094/s（720p 无输入）**，相对完整版 720p **$0.157/s** 约省四成；带参考视频务必按「总时长」规则复算，勿把 $0.063 当最终单价。成片交付若要 1080p/更长单镜/原生音频，仍回完整版 4.0 或其它带音频模型（如 Seedance 2.5）。
- **产能**：从年订专属变为全用户+API+MCP/CLI+Adobe 插件，剪辑时间线与 agent 管线可直接调 Flash，适合竖屏短剧多版本试镜；官方未公布公开 API 的并发/队列上限，大批量排期仍需实测。
- **过审 / 分账**：本轮无平台过审或分账条款。

## 原文摘录

### @Kling_ai（2026-11-04 15:00 UTC）

> Kling 4.0 Flash Is Now Fully Available! ⚡
>
> Kling 4.0 Flash is now available to everyone on the Kling AI website and via API.
>
> You can also access it through MCP, CLI, and AI plugins, bringing greater flexibility to your video creation workflows. With Kling plugins for …

### 官方 API Updates（2026-11-04）

> [Video Generation] Kling 4.0 Flash API Is Now Available, with Native Video Generation up to 20s
>
> - Supports video generation from 3 to 20 seconds at 720P resolution.
> - … Request paths: /text-to-video/kling-4.0-flash, /image-to-video/kling-4.0-flash, and /omni-video/kling-4.0-flash.
> - Billing is based on total duration. … See the pricing page.

### 官方价目（Video pricing）

> Kling 4.0 Flash | No Input Video | 0.6 Units ($0.094) /s | 720P only
> Kling 4.0 Flash | With Input Video … | 0.4 Units ($0.063) /s | total duration rules apply
> Kling 4.0 | No Input Video | 1.0 Unit ($0.157) /s (720P)

### TheReelStack（2026-11-04）

> Kling announced on Nov 4 that Kling 4.0 Flash… is now available to every user on the Kling website and through the API. It can also be reached through MCP, a CLI and plugins for Photoshop, Premiere Pro and After Effects.
>
> What we don't know yet. The announcement doesn't list Flash prices or limits next to full Kling 4.0. Check the API pricing page before you switch batch jobs over.

## 来源

- [X · @Kling_ai] Kling 4.0 Flash Is Now Fully Available（2026-11-04 15:00 UTC）https://x.com/Kling_ai/status/2117995299591319932
- [Kling API Updates] 11/04/2026 Flash API（已打开）https://kling.ai/document-api/updates/api.md
- [Kling Video Pricing] Flash / 4.0 价目表（已打开）https://kling.ai/document-api/pricing/base/video.md
- [Kling 4.0 User Guide] Flash 规格表 3–20s / 720p（对照）https://kling.ai/quickstart/kling-4-model-user-guide
- [OrcaRouter] Kling 4.0 Flash Goes GA: $0.094/s and a 720p Ceiling（2026-11-04；已打开）https://www.orcarouter.ai/blog/kling-4-0-flash-general-availability
- [TheReelStack] Kling 4.0 Flash is open to everyone…（2026-11-04；已打开）https://thereelstack.com/lab/kling-4-0-flash-generally-available-api-mcp-plugins

## 口径警告

- **≠** 已入库「Runway Kling 4.0 促销」（那是 Runway 渠道折扣，截止约 11-30 UTC）。
- **≠** 10-28 完整版 Kling 4.0 API 全量（最长 30s / 含 1080p）；本轮是 **Flash** 层。
- Flash **720p 天花板 + 最长 20s + 无原生音频价目行**：适合草稿与竖屏预览，不适合当成片母带唯一来源。
- 「有输入视频 $0.063/s」在输入≤输出时按输出×2 计费，有效成本常 **高于** 无输入 $0.094/s。
- 官方未公布公开 API 速率/并发上限；大批量产能断言需实测。
