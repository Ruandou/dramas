# 天工开物 · Agent / CLI 指引

## 改剧本 / 对白 / 字幕（顺序强制）

1. **主剧本** `短剧剧本_天工开物_36集.md`
2. **分集剧本** `剧本/EP##_*.md`
3. `python3 script/storyboard_to_seedance.py EP##`
4. `剧本/EP##_segments.yaml`
5. 声音卡、规范、`trial_notes` 等

**不要**先改 `segments.yaml`。详见 [`制片规范.md`](./制片规范.md) §3.1。

---

## 推荐：用 volc-ark MCP（Key 已在 mcp.json，不用再 export）

在对话里说即可，例如：

> 用 `ark_drama_pull` 拉取 EP01 并拼集：`episode=EP01`, `concat=true`

| MCP 工具                 | 扣费   | 说明                                              |
| ------------------------ | ------ | ------------------------------------------------- |
| **`ark_drama_pull`**     | 否     | git pull + 按 `tasks.json` 下载同事段落（24h 内） |
| `ark_list_tasks`         | 否     | 查 `assets/generated/EP##/tasks.json`             |
| `ark_seedance_download`  | 否     | 按单个 `task_id` 下到指定路径                     |
| `ark_seedance_create` 等 | **是** | 仅用户明确要求时                                  |

`mcp.json` 建议：

```json
"volc-ark": {
  "env": {
    "ARK_API_KEY": "…",
    "DRAMA_PROJECT_ROOT": "/绝对路径/dramas/天工开物"
  }
}
```

未传 `project_root` 时，`ark_drama_pull` 用 `DRAMA_PROJECT_ROOT` 或默认 `dramas/天工开物`。

---

## 终端 CLI：`tgkw`（可选）

会自动尝试读取 **`.cursor/mcp.json`** 里 `volc-ark` 的 Key（与 MCP 同源）。

```bash
cd dramas/天工开物
./tgkw pull EP01 --concat
```

等价于 MCP `ark_drama_pull`（episode=EP01, concat=true）。

### 其它子命令

```bash
./tgkw check EP01
./tgkw tasks EP01
./tgkw concat EP01
```

---

## 协作前提

1. 同事 push `assets/generated/EP01/tasks.json`
2. 你在 **24h 内** pull / `ark_drama_pull`
3. 勿覆盖正式 `EP##-SEG*.mp4` 占位

文档：[`docs/视频资产管理.md`](docs/视频资产管理.md) · [`docs/团队协作.md`](docs/团队协作.md)
