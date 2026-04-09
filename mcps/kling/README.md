# 可灵AI视频生成 · Cursor MCP

在 Cursor 里通过 MCP 调用 **可灵AI（Kling）视频生成 API**。认证方式：**Bearer Token（API Key）**。

## 前置条件

1. **Node.js 18+**
2. **Python 3**（内置 `urllib` 无需额外依赖）

## 安装依赖

```bash
cd mcps/kling
npm install
```

## 配置 Cursor

将下面合并到 **用户目录** `~/.cursor/mcp.json` 或 **项目** `.cursor/mcp.json`（任选其一）。

```json
{
  "mcpServers": {
    "kling": {
      "command": "/你的绝对路径/.nvm/versions/node/vXX.X.X/bin/node",
      "args": ["/你的绝对路径/Movies/demo1/mcps/kling/index.mjs"],
      "cwd": "/你的绝对路径/Movies/demo1/mcps/kling",
      "env": {
        "KLING_AK": "你的API Key",
        "KLING_SK": "你的Secret Key"
      }
    }
  }
}
```

- **路径**：把 `demo1`、`.nvm/.../node` 换成你本机路径。
- **macOS 必看**：Cursor 从「程序坞」启动时 **PATH 里往往没有 nvm**，请用终端执行 `which node`，把 **node 的绝对路径** 填进 `command`。

改完后 **重启 Cursor** 或 **Developer: Reload Window**。

## 提供的工具

| 工具名 | 作用 |
|--------|------|
| `kling_docs` | 返回可灵AI接入文档链接 |
| `kling_auth` | 设置/保存 API 凭证到 `~/.kling_credentials` |
| `kling_image_to_video` | 图生视频：支持单图或多图主体（最多4张），传入图片路径和描述，生成动态视频 |
| `kling_text_to_video` | 文生视频：传入描述，生成视频 |
| `kling_query_task` | 查询任务状态：传入 `task_id`，返回视频链接 |
| `kling_wait_task` | 等待任务完成：轮询直到生成完毕 |
| `kling_download_video` | 下载视频到本地（默认 `video/kling`） |
| `kling_list_tasks` | 列出归档的任务记录 |

## 任务归档

任务提交后会自动保存到 `video/kling_tasks/tasks.json`，包含：
- `task_id` - 任务ID
- `type` - 任务类型（image_to_video / text_to_video）
- `params` - 提交参数
- `status` - 状态（pending / processing / completed / failed）
- `video_url` - 生成完成后视频链接
- `created_at` / `updated_at` - 时间戳

## API 信息

**官方文档**：https://klingapi.com/zh/docs

**端点**：
- `POST /v1/videos/text2video` - 文生视频
- `POST /v1/videos/image2video` - 图生视频
- `GET /v1/videos/{task_id}` - 查询任务状态

**模型**：
| 模型 | 说明 |
|------|------|
| `kling-video-o1` | 统一多模态模型 |
| `kling-v3-omni` | **3.0全能，原生音画同出、多镜头** |
| `kling-v3` | 3.0基础版，支持多镜头 |
| `kling-v2.6-pro` | 2.6专业版 |
| `kling-v2.6-std` | 2.6标准版 |
| `kling-v2.5-turbo` | 2.5快速版 |

## 安全

- 密钥只放在 **环境变量** 或本机 `mcp.json`（已加入 `.gitignore` 时勿把含密钥文件提交）。
- 仓库内仅保留 `mcp.json.example`（无真实密钥）。

## 故障排查

- **MCP 一直红 / spawn node ENOENT**：没用到 node 绝对路径（见上文 macOS + nvm）。
- **401 鉴权失败**：检查 KLING_AK / KLING_SK 是否正确。
- **任务失败**：检查账户余额，新用户注册送 $1 额度。
