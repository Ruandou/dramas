# 火山引擎即梦 / 视觉 API · Cursor MCP

在 Cursor 里通过 MCP 调用 **火山引擎「视觉智能」OpenAPI**（与即梦视频文档中的 Action/Body 一致）。认证方式遵循官方 [接入说明](https://www.volcengine.com/docs/6444/69732?lang=zh)：**访问密钥 AK/SK**。

## 前置条件

1. **Node.js 18+**（本机已有 `node` 即可）  
2. **Python 3** + 旧版 `volcengine` SDK（带 `volcengine.visual.VisualService`）：

   ```bash
   pip3 install 'volcengine>=1.0.130,<2' --user
   ```

3. 火山控制台创建 **API 访问密钥**，并开通 **即梦 AI · 视频生成** 等产品（见 [即梦视频 3.0 Pro 接口文档](https://www.volcengine.com/docs/85621/1777001?lang=zh)）。

4. **账户有余额**（可用余额为 0 时调用会失败）。

## 安装依赖（在项目内）

```bash
cd mcp/volc-jimeng
npm install
```

## 配置 Cursor

将下面合并到 **用户目录** `~/.cursor/mcp.json` 或 **项目** `.cursor/mcp.json`（任选其一）。把密钥换成你在控制台创建的 AK/SK，**勿提交到 Git**。

```json
{
  "mcpServers": {
    "volc-jimeng": {
      "command": "/你的绝对路径/.nvm/versions/node/vXX.X.X/bin/node",
      "args": ["/你的绝对路径/Movies/demo1/mcp/volc-jimeng/index.mjs"],
      "cwd": "/你的绝对路径/Movies/demo1/mcp/volc-jimeng",
      "env": {
        "VOLC_PYTHON": "/usr/bin/python3",
        "VOLC_ACCESS_KEY": "你的AccessKey",
        "VOLC_SECRET_KEY": "你的SecretKey"
      }
    }
  }
}
```

- **路径**：把 `demo1`、`.nvm/.../node` 换成你本机路径。  
- **macOS 必看**：Cursor 从「程序坞」启动时 **PATH 里往往没有 nvm**，`"command": "node"` 会找不到。请用终端执行 `which node`，把 **node 的绝对路径** 填进 `command`。  
- **cwd**：指向 `mcp/volc-jimeng` 目录，避免依赖解析异常。  
- **VOLC_PYTHON**：固定为系统 `python3`（与 `pip3 install --user` 安装 volcengine 的解释器一致）。  
- **VOLC_DOWNLOAD_DIR**（可选）：不填时，下载工具默认写入本仓库 `video/generated`。  
- **VOLC_PROJECT_ROOT**（可选）：不填时，相对路径以「含 `mcp/volc-jimeng` 的仓库根」为准。  
- **VOLC_MERGE_OUTPUT_DIR**（可选）：`volc_merge_local_videos` 输出目录，默认 `video/output`。  
- **FFMPEG_PATH**（可选）：`ffmpeg` 可执行文件路径，默认在 `PATH` 中查找。  
- **`ARK_API_KEY`（可选）：** 方舟 **Bearer** API Key，用于 **`ark_list_generation_tasks`** / **`ark_download_ark_videos`**（与视觉 AK/SK 不同，在方舟控制台创建）。  
- **`local_render_pipeline`**：依赖 **`VOLC_PYTHON`** 与 **`VOLC_PROJECT_ROOT`**（不设则默认 MCP 所在仓库根），以运行 `video/automation/local_pipeline.py`。

改完后 **重启 Cursor** 或 **Developer: Reload Window**。

## 提供的工具

| 工具名 | 作用 |
|--------|------|
| `volcengine_docs` | 返回接入说明、即梦接口等文档链接 |
| `volc_visual_submit` | 传入 `action`、`version`（可选）、`body`（对象），由 Python 脚本签名并 POST |
| `volc_visual_query` | 查询异步任务：传入 `task_id`，可选 `req_key`（默认 `jimeng_ti2v_v30_pro`），内部调用 `CVSync2AsyncGetResult` |
| `volc_download_video` | 传入 `url`（直链）与可选 `filename`（中文名可），保存为 MP4 到 `video/generated`（或环境变量 `VOLC_DOWNLOAD_DIR`） |
| `volc_merge_local_videos` | 本机 **ffmpeg** 按顺序拼接多条 MP4（优先流复制），输出到 `video/output`；需已安装 `ffmpeg`（如 `brew install ffmpeg`） |
| `local_render_pipeline` | 调用 **`video/automation/local_pipeline.py`**：拼接 + 可选 BGM + 可选 **软字幕轨**（mov_text）；传入 `config_path` 或 `clips`+`output` 等 |
| `local_tts_edge_batch` | 调用 **`video/automation/tts_batch_edge.py`**：按行生成 `001.mp3`…；需 `pip install edge-tts`；参数 `lines_path`、`out_dir`、可选 `voice` |
| `local_mix_tts_srt` | 调用 **`video/automation/mix_tts_from_srt.py`**：按 SRT 起点把 TTS mp3 混进成片；参数 `video_path`、`srt_path`、`tts_dir`、`output_path`，可选 `original_volume`、`dry_run` |
| `ark_list_generation_tasks` | 方舟 **`GET …/api/v3/contents/generations/tasks`**（近 7 天），需 **`ARK_API_KEY`**；可选 `status`、`model`、`page_size`、`max_pages` |
| `ark_download_ark_videos` | **`ark_generation_tasks.py download`**；可选 **`ep01_names`** 按时间序重命名 14 镜；需 **`ARK_API_KEY`** |
| `volc_list_tasks` | 列出本地归档的任务记录 |

**重要：** `action`、`version`、**body 内字段**（如 `req_key`、`prompt`、图生视频 URL 等）必须与控制台当前 **即梦视频 3.0 Pro** 接口文档一致；不同版本可能不同，请复制文档中的示例再改。

**文生视频**一般只需 `prompt` 等，**无需**传图。**图生视频 / 首帧**需在 `body` 里按文档增加图片相关字段；本 MCP 不会自动上传你电脑里的素材文件。

## 安全

- 密钥只放在 **环境变量** 或本机 `mcp.json`（已加入 `.gitignore` 时勿把含密钥文件提交）。  
- 仓库内仅保留 `mcp.json.example`（无真实密钥）。

## 任务归档

`volc_visual_submit` 提交任务后会自动保存到 `video/jimeng_tasks/tasks.json`，包含：
- `task_id` - 任务ID
- `type` - 提交时使用的 action
- `params` - 提交参数
- `status` - 状态
- `video_url` - 生成完成后视频链接
- `created_at` / `updated_at` - 时间戳

使用 `volc_list_tasks` 查看归档记录。

## 故障排查

- **MCP 一直红 / spawn node ENOENT**：几乎总是 **没用到 node 绝对路径**（见上文 macOS + nvm）。  
- **`ModuleNotFoundError: volcengine`**：对 `VOLC_PYTHON` 指向的解释器执行：`pip3 install 'volcengine>=1.0.130,<2' --user`。  
- **`no such api`**：核对 Action 是否与 [接口文档](https://www.volcengine.com/docs/85621/1777001?lang=zh) 一致；本脚本会动态注册 Action。  
- **鉴权失败 / 余额**：检查 AK/SK、即梦是否开通、账户余额。  
- **升级 Node 后 MCP 挂了**：nvm 路径会变，把 `command` 里的 node 路径改成新的 `which node`。  
- **`volc_merge_local_videos` 报错找不到 ffmpeg**：安装 `brew install ffmpeg`，或设置 `FFMPEG_PATH`。  
- **`local_render_pipeline` 找不到脚本**：确认 `VOLC_PROJECT_ROOT` 指向含 `video/automation/` 的仓库根；本机需 `python3` 与 `ffmpeg`。  
- **`local_tts_edge_batch` 报 `edge_tts` 未安装**：对 `VOLC_PYTHON` 执行 `pip3 install edge-tts --user`（或项目 `video/automation/requirements.txt`）。  
- **`local_mix_tts_srt` 条数不一致**：SRT 中非空字幕条数须等于 `tts_dir` 里「纯数字文件名」的 `.mp3` 个数（升序后与字幕顺序一一对应）。  
- **`ark_*` 401 / 无数据**：在 `mcp.json` 的 `env` 中配置 **`ARK_API_KEY`**（方舟 API Key）；任务约保留 **7 天**，视频直链约 **24h** 有效。  
- **`ark_download_ark_videos` + ep01_names 镜号错位**：该模式按 **创建时间升序** 取前 14 条成功任务；若期间还有别的生成，请先用 `ark_list_generation_tasks` 核对 `id` / 时间，或加 `model` 筛选。

## 方舟任务列表（可选）

在 MCP `env` 中增加：

```json
"ARK_API_KEY": "你的方舟APIKey"
```

命令行等价：`python3 video/automation/ark_generation_tasks.py list|download …`。
