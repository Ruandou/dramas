# 天工开物 · 视频素材目录

生成 Seedance 视频前，按顺序备齐三层素材：

## 1. 定妆与场景（全剧复用）

```bash
# 查看待生成清单与英文 Prompt
cat assets/looks/seedream_batch.yaml
cat assets/scenes/seedream_batch.yaml
```

| 目录 | 命名 | 说明 |
|------|------|------|
| `looks/` | `CHAR-001-L01.png` | 角色卡 L01 锚点；L02+ 基于 L01 图生图 |
| `scenes/` | `SCENE-001.png` | 场景卡片空景，无人物 |

## 2. 镜头首帧（每镜一张）

```bash
python3 script/storyboard_keyframe_prompts.py EP01
cat assets/keyframes/EP01/seedream_prompts.yaml
```

输出：`assets/keyframes/EP##/EP##-Sxx_first.png`

## 3. 提交 Seedance

```bash
python3 script/storyboard_submit_seedance.py EP01 --check-only
export ARK_API_KEY=...
python3 script/storyboard_submit_seedance.py EP01          # 写出 configs/seedance_requests/
python3 script/storyboard_submit_seedance.py EP01 --submit # 本地图自动 base64，无需图床
```

或使用 MCP **`volc-ark`** 的 `ark_seedance_shots` / CLI `mcps/volc-ark/scripts/ark_seedance_video.py shots`。

成片：`assets/generated/EP##/` · 方舟任务归档 `video/ark_tasks/tasks_video.json`（与 `volc-jimeng` 的 `jimeng_tasks` 分开）

**禁止**向其他剧的 `generated/` 目录写入占位 MP4。
