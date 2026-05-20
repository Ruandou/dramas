# 天工开物 · 视频素材目录

**默认流程（2026-05-20）**：有声 **段落** `segments.yaml` → Seedance 2.0，见 [`../docs/Seedance2_有声段落流水线.md`](../docs/Seedance2_有声段落流水线.md)。

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
cd darams/天工开物
python3 script/storyboard_submit_segments.py EP01 --check-only
python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b   # dry-run → configs/
export ARK_API_KEY=...
python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b --submit
```

或仓库根：`python3 mcps/volc-ark/scripts/ark_seedance_video.py segments EP01 --project-root darams/天工开物`

成片：`assets/generated/EP##/EP01-SEGxx.mp4`

**任务登记（方案 A）**：`assets/generated/EP##/tasks.json` 等，见 [`TASKS.md`](./TASKS.md)。提交前建议 `export DRAMA_PROJECT_ROOT=$(pwd)`。

```bash
python3 mcps/volc-ark/scripts/project_task_archive.py list --project-root . --episode EP01
```

```bash
# 集级顺接（试跑通过后）
bash script/ffmpeg_concat_episode.sh EP01
```

**禁止**向其他剧的 `generated/` 写入占位 MP4。

## 5. 镜级（legacy）

`storyboard_submit_seedance.py` + `EP##_shots.yaml` 仍可用于对照；非默认交付路径。
