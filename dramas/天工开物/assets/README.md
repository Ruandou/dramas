# 天工开物 · 视频素材目录

**默认流程（2026-05-20）**：有声 **段落** `segments.yaml` → Seedance 2.0，见 [`../docs/Seedance2_有声段落流水线.md`](../docs/Seedance2_有声段落流水线.md)。

**视频怎么管（目录、拼接、验收、重跑）**：[`../docs/视频资产管理.md`](../docs/视频资产管理.md)  
**拉同事成片**：Cursor 用 MCP **`ark_drama_pull`**（Key 已在 mcp.json）· 终端 [`../AGENTS.md`](../AGENTS.md) `./tgkw pull EP01 --concat`

## 1. 定妆与场景（全剧复用，段落必用）

| 目录 | 命名 | 说明 |
|------|------|------|
| `looks/` | `CHAR-001-L01.png` | 角色卡 L01 锚点 |
| `scenes/` | `SCENE-001.png` | 场景卡片空景 |

```bash
ls -lh assets/looks/*.png assets/scenes/*.png
```

## 2. 声音锚点（可选，漂移时补）

| 目录 | 说明 |
|------|------|
| `voices/` | `CHAR-001_ref.wav` 等，挂 API `reference_audio`；试点可先仅 `voice_prompt` |

见 [`../资产/声音卡.md`](../资产/声音卡.md)。

## 3. 镜头首帧（可选，镜级旧流程）

镜级 `i2v` / `storyboard_submit_seedance.py` 才需要 `keyframes/EP##/*_first.png`。  
**段落流水线不依赖首帧。**

## 4. 提交 Seedance（段落）

```bash
cd dramas/天工开物
python3 script/storyboard_submit_segments.py EP01 --check-only
python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b   # dry-run → configs/
export ARK_API_KEY=...
python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b --submit
```

或仓库根：`python3 mcps/volc-ark/scripts/ark_seedance_video.py segments EP01 --project-root dramas/天工开物`

成片：`assets/generated/EP##/EP01-SEGxx.mp4`

**任务登记（方案 A）**：`assets/generated/EP##/tasks.json` 等，见 [`TASKS.md`](./TASKS.md)。提交前建议 `export DRAMA_PROJECT_ROOT=$(pwd)`。

```bash
python3 mcps/shared/project_task_archive.py list --project-root . --episode EP01
```

```bash
# 一键拉同事段落（先 git pull 同事提交的 tasks.json，24h 内从方舟下）
bash script/pull_episode.sh EP01 --concat

# 仅拼集（本地段已齐）
bash script/ffmpeg_concat_episode.sh EP01
```

**禁止**向其他剧的 `generated/` 写入占位 MP4。

## 5. 镜级（legacy）

`storyboard_submit_seedance.py` + `EP##_shots.yaml` 仍可用于对照；非默认交付路径。
