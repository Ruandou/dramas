# 遗留：仓库级方舟归档（勿用于新短剧）

新短剧请用 **方案 A**：任务写在 **`{短剧根}/assets/`** 下，见各剧 `assets/TASKS.md`。

本目录仅作 **未设置 `DRAMA_PROJECT_ROOT`** 时的回退；天工开物等请设环境变量或 `--project-root`。

```bash
export DRAMA_PROJECT_ROOT=/path/to/darams/天工开物
python3 mcps/volc-ark/scripts/project_task_archive.py migrate-legacy-video \
  --project-root "$DRAMA_PROJECT_ROOT"
```
