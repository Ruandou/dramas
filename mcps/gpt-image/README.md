# gpt-image · OpenAI 兼容中转图生图 CLI

GetGoAPI（`https://api.getgoapi.com`，OpenAI 兼容协议）gpt-image-2 文生图/图生图 CLI。

| 能力 | 模型示例 | 接口 |
|------|----------|------|
| **gpt-image-2** 文生图/图生图 | `openai/gpt-image-2`（`GPT_IMAGE_MODEL` 可覆盖） | `POST https://api.getgoapi.com/v1/images/generations` |

## 用法

```bash
python3 mcps/gpt-image/scripts/gpt_image.py docs                 # 文档/默认配置
python3 mcps/gpt-image/scripts/gpt_image.py generate --prompt "..." --output out.png
python3 mcps/gpt-image/scripts/gpt_image.py generate --prompt "..." \
  --image-url assets/looks/CHAR-001-L01.png --tier 2k --quality high
python3 mcps/gpt-image/scripts/gpt_image.py batch --yaml assets/looks/gpt_image_batch.yaml --dry-run
python3 mcps/gpt-image/scripts/gpt_image.py reconcile --yaml assets/looks/gpt_image_batch.yaml --project-root dramas/<剧名>
```

命令与 `mcps/volc-ark/scripts/ark_seedream_image.py` 同构：`generate` / `batch` / `docs` / `reconcile`。

## 环境变量

| 变量 | 说明 |
|------|------|
| `GPT_IMAGE_API_KEY` | 必填，Bearer 鉴权（兼容回退 `OPENAI_API_KEY`） |
| `GPT_IMAGE_BASE_URL` | 默认 `https://api.getgoapi.com`（兼容回退 `OPENAI_BASE_URL`） |
| `GPT_IMAGE_MODEL` | 默认 `openai/gpt-image-2` |
| `GPT_IMAGE_QUALITY` | `low` / `medium` / `high` / `auto`（默认 auto） |
| `GPT_IMAGE_SIZE_TIER` | `standard` / `2k` / `4k`（默认 standard） |

## 模型选择与计费

数据来源：`GET https://api.getgoapi.com/api/pricing` 实测（2026-08）。

| 模型 | 计费 | 单价 | 说明 |
|------|------|------|------|
| `openai/gpt-image-2`（默认） | 按次（quota_type=1） | **$0.10/张 ≈ ¥0.72** | 官方渠道（vendor 1）一口价，与尺寸/质量无关，费用可预测 |
| `gpt-image-2` | 按额度（quota_type=0） | 倍率 2.5 / 输出倍率 6 | 平台渠道，单张按估算 token 浮动，中小图可能更省，大图可能更贵 |

官方 gpt-image-2 为按 token 计费（$8/1M 输入、$30/1M 输出），单张实际成本约 $0.005–$0.211（随尺寸/质量）；平台按次价 $0.10 是中间档的一口价。

## 尺寸规格

gpt-image-2 约束：边长 16 的倍数、最大边长 ≤3840、长边/短边 ≤3:1、总像素 655,360~8,294,400。

| 比例 | standard | 2k | 4k |
|------|----------|-----|-----|
| 9:16 | 1024x1536 | 1152x2048 | 2160x3840 |
| 16:9 | 1536x1024 | 2048x1152 | 3840x2160 |
| 1:1 | 1024x1024 | 2048x2048 | 2880x2880 |
| 4:3 | 1280x960 | 2048x1536 | 3264x2448 |
| 3:4 | 960x1280 | 1536x2048 | 2448x3264 |

`--size 2048x1152` 显式指定时优先生效；`--tier` 仅在未给 `--size` 时映射比例。

## 特性

- **参考图**：`--image-url` 支持本地路径（自动转 data URI）或 https URL，≤16 张，按数组传给 `image` 字段
- **去重防双扣**：指纹去重 + submitting 卡位与 Seedream 同一套基建（`mcps/shared/dedup.py`），kind=`gpt_image`
- **任务归档**：`--project-root`（或 `DRAMA_PROJECT_ROOT`）下写 `assets/tasks_gpt_image.json`
- **CDN registry**：输出到 `assets/looks/` 或 `assets/scenes/` 时自动更新 `cdn_urls.json`
- **安全**：`--dry-run` 不扣费；真实出图需用户明确授权；`--force` 需 `ARK_ALLOW_FORCE=1`
- **YAML 注意**：`ratio: 9:16` 不加引号会被 PyYAML 按六十进制解析为整数 556，CLI 已自动还原，但建议写 `ratio: "9:16"`

## 目录结构

```
mcps/gpt-image/
├── README.md
└── scripts/
    └── gpt_image.py        # CLI（依赖 mcps/shared/ 公共基建层）
```

通用媒体基建（`media_utils` / `dedup` / `archive` / `project_task_archive` / `cdn_registry`）位于 **`mcps/shared/`**，由各 CLI 通过 sys.path 引导引用，勿在脚本目录下重建同名模块。
