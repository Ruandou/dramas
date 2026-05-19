# volc-ark · 火山方舟（图 + 视频）

独立于 `volc-jimeng`（视觉 AK/SK + 即梦 4.0）的 **方舟 Bearer API** 工具包。

| 能力 | 模型示例 | 接口 |
|------|----------|------|
| **Seedream 5.0 lite** 文生图 | `doubao-seedream-5.0-lite` | `POST /api/v3/responses` |
| **Seedance 2.0 fast** 视频 | `doubao-seedance-2-0-fast-260128` | `POST /api/v3/contents/generations/tasks` |

## 图床

**不需要。** 本地 `assets/` 图片在提交时自动转为 **data URI**（base64）写入 API；仅当参考图本身已是 `https://` 或 `data:` 时原样使用。

## 任务归档（与 volc-jimeng 同级）

每次成功 **创建/提交** 会写入仓库：

```
video/ark_tasks/
├── tasks_image.json   # Seedream
└── tasks_video.json   # Seedance
```

与 `video/jimeng_tasks/`（视觉 AK/SK 即梦 4.0）分开存放。`get` / `wait` 会回写 `status`、`video_url`。

| MCP 工具 | 说明 |
|----------|------|
| `ark_list_tasks` | 读本地 `video/ark_tasks/` |
| `ark_seedance_list` | 读方舟云端任务列表（近约 7 天） |

## 环境变量（MCP 配置）

| 变量 | 说明 |
|------|------|
| `ARK_API_KEY` | 方舟 API Key（**MCP 只需这一项**） |

相对路径默认相对仓库根（`mcps/volc-ark` 上两级）。工作区不是仓库根时再设 `ARK_PROJECT_ROOT`。

## Cursor MCP 工具一览

| 工具 | 作用 |
|------|------|
| `ark_seedream_*` | 图片 |
| `ark_seedance_*` | 视频 |
| `ark_list_tasks` | 本地归档 |

**注意：** 调用消耗方舟余额；Agent 应在用户明确授权后再提交生成。

详见各 `scripts/*.py` 的 `docs` 子命令。
