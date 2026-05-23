# 超雄重生1995 · 视频素材目录

> 现代刑侦重生剧，主角回到 1995 年，以超前认知破获连环悬案。

**默认流程**：有声 **段落** `EP##_segments.yaml` → Seedance 2.0 生成视频段落。

**流水线**：`剧本/EP##/*.md` 分镜剧本 → `EP##_segments.yaml` → Seedance 2.0 → `assets/generated/EP##/EP##-SEG*.mp4`

## 1. 定妆照（全剧复用，段落必用）

| 目录 | 命名 | 说明 |
|------|------|------|
| `looks/` | `CHAR-###-L##.png` | 角色定妆参考图；Seedance 用于面部一致性锚定 |
| `scenes/` | `SCENE-###.png` | 场景空景参考图；空间一致性锚点（1995 年代街道、老式刑侦办公室等） |

```bash
ls -lh assets/looks/*.png assets/scenes/*.png
```

## 2. 道具参考

| 目录 | 命名 | 说明 |
|------|------|------|
| `props/` | 自定义 | 道具参考图：证据物证、武器凶器、档案文件等 1995 年代刑侦相关实物 |

## 3. 声音锚点（可选，漂移时补）

| 目录 | 说明 |
|------|------|
| `voices/` | `CHAR-###_ref.wav` 等，挂 API `reference_audio`；用于跨集保持角色音色一致 |

## 4. 镜头首帧（可选，镜级旧流程）

| 目录 | 说明 |
|------|------|
| `keyframes/` | `EP##/*_first.png`，仅 `i2v` 镜级流程使用 |

**段落流水线不依赖首帧。**

## 5. 生成视频输出

| 目录 | 说明 |
|------|------|
| `generated/EP##/` | Seedance 视频段落输出，如 `EP01-SEG01.mp4` |
| `generated/EP##/tasks.json` | 任务归档 JSON，记录 task_id 便于重新下载 |

### 提交 Seedance（段落）

```bash
cd darams/超雄重生1995
python3 script/storyboard_submit_segments.py EP01 --check-only
python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG01 --submit
```

成片：`assets/generated/EP##/EP##-SEGxx.mp4`

### 拉取 & 拼接

```bash
bash script/pull_episode.sh EP01 --concat
bash script/ffmpeg_concat_episode.sh EP01
```

## ⚠️ 安全警告

- **禁止**向 `generated/` 写入占位视频、测试条、纯色条等文件
- **禁止**覆盖已有即梦/Seedance 导出的正式 MP4
- 自动化脚本测试输出必须写到 `generated/_placeholders/`（需自建），使用不同文件名
- 素材丢失时优先从方舟任务历史或 `tasks.json` 中记录的 task_id 重新下载
