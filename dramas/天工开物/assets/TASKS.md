# 任务归档（方案 A）

所有 API 任务登记在 **本剧 `assets/`**，与成片同目录，不写入仓库 `video/ark_tasks/`。

| 类型 | 路径 |
|------|------|
| Seedance 视频（按集） | `generated/EP01/tasks.json` |
| Seedream 出图 | `tasks_seedream.json` |
| 即梦/视觉 图 | `tasks_jimeng_image.json` |
| 即梦/视觉 视频 | `tasks_jimeng_video.json` |
| Kling | `tasks_kling.json` |

## 环境变量

```bash
export DRAMA_PROJECT_ROOT=/path/to/dramas/天工开物
```

`mcp.json` 的 `volc-ark` / `volc-jimeng` 建议加上述 `env`。

## 查询

```bash
python3 mcps/shared/project_task_archive.py list \
  --project-root dramas/天工开物 --episode EP01

python3 mcps/shared/project_task_archive.py list \
  --project-root dramas/天工开物 --kind seedream
```

## 从旧 task_log.jsonl 导入

```bash
python3 mcps/shared/project_task_archive.py import-jsonl \
  dramas/天工开物/assets/generated/EP01/task_log.jsonl \
  --project-root dramas/天工开物 --episode EP01
```
