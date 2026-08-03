# volc-ark · 火山方舟（图 + 视频）

独立于 `volc-jimeng`（视觉 AK/SK + 即梦 4.0）的 **方舟 Bearer API** 工具包。

| 能力 | 模型示例 | 接口 |
|------|----------|------|
| **Seedream 5.0 lite** 文生图 | `doubao-seedream-5-0-lite-260128`（`ARK_SEEDREAM_MODEL` 可覆盖） | `POST /api/v3/images/generations` |
| **Seedance 2.0 fast** 视频 | `doubao-seedance-2-0-fast-260128` | `POST /api/v3/contents/generations/tasks` |

> **gpt-image-2 CLI** 已独立到 [`mcps/gpt-image/`](../gpt-image/README.md)（OpenAI 兼容中转，走 GetGoAPI）。
> 通用媒体基建（`media_utils` / `dedup` / `archive` / `project_task_archive` / `cdn_registry`）已抽到 **`mcps/shared/`**，本目录脚本通过 sys.path 引导引用，请勿在 `scripts/` 下重建同名模块。

## 图床

**不需要。** 本地 `assets/` 图片在提交时自动转为 **data URI**（base64）写入 API；仅当参考图本身已是 `https://` 或 `data:` 时原样使用。

## 任务归档（方案 A · 推荐）

设置 **`DRAMA_PROJECT_ROOT`**（短剧根，如 `dramas/天工开物`）后，任务写入该剧 `assets/`：

```
assets/generated/EP01/tasks.json   # Seedance 按集
assets/tasks_seedream.json
assets/tasks_jimeng_*.json         # 即梦（volc-jimeng，同 env）
assets/tasks_kling.json            # Kling（同 env）
```

未设 `DRAMA_PROJECT_ROOT` 时回退 `video/ark_tasks/`（遗留）。详见 `project_task_archive.py`、各剧 `assets/TASKS.md`。

| MCP 工具 | 说明 |
|----------|------|
| **`ark_drama_pull`** | **拉同事段落**（git pull + tasks.json 下载，**不扣费**，用 MCP 已配 Key） |
| `ark_list_tasks` | 读 `DRAMA_PROJECT_ROOT` 下 assets；可传 `project_root` / `episode` |
| `ark_seedance_list` | 读方舟云端任务列表（近约 7 天） |

## 环境变量（MCP 配置）

| 变量 | 说明 |
|------|------|
| `ARK_API_KEY` | 方舟 API Key（**MCP 只需这一项**） |

| `DRAMA_PROJECT_ROOT` | 短剧根（**任务归档方案 A**，与 `ARK_PROJECT_ROOT` 等价） |

相对路径默认相对仓库根。短剧流水线务必设 `DRAMA_PROJECT_ROOT`。

## Cursor MCP 工具一览

| 工具 | 作用 |
|------|------|
| **`ark_drama_pull`** | 拉短剧同事成片（**推荐**，无需终端 export Key） |
| `ark_seedream_*` | 图片 |
| `ark_seedance_*` | 视频 |
| `ark_list_tasks` | 本地归档 |

**注意：** 调用消耗方舟余额；Agent 应在用户明确授权后再提交生成。

详见各 `scripts/*.py` 的 `docs` 子命令。
