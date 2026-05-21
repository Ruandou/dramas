# EP01 声音试点记录（路线一 · 仅提示词）

> 日期：2026-05-20

## 试跑段落

| 段 | task_id | 成片 | 时长 API | generate_audio |
|----|---------|------|----------|----------------|
| EP01-SEG04b | cgt-20260520142142-bv7z5 | EP01-SEG04b.mp4 (~4.9MB) | 10s | true |
| EP01-SEG06b | cgt-20260520142555-s8js5 | EP01-SEG06b.mp4 (~4.4MB) | 8s | true |

## 验收（2026-05-20）

- [x] 全集 `EP01_full.mp4` 耳听：**声音还可以**
- [x] **阶段 1 通过** — 暂不补 `reference_audio` 锚点
- 未挂 `reference_audio`；宋知行 `voice_prompt` 跨段一致  
- **字幕**：全段对白/字卡 Seedance 画面简体底字幕；仅 SEG01a 无对白无字幕

## 全集生成

- 11 段顺接 → `EP01_full.mp4`（约 1:39，~50MB）
- `concat_list.txt` 按当前 `EP01_segments.yaml`（无单独 SEG02b）
- 若需合并版 SEG02（S07–S09 一条）：重跑 `EP01-SEG02` 后再 `ffmpeg_concat_episode.sh EP01`

## 剧情/道具反馈（2026-05-20）

- C 段抄锤：①墙角锤小、贴身锤大 → **道具尺度漂移**；②**打手先抄锤** → 角色动作绑错（上一镜打手对白，模型把「抄起」给了图2）。已合并 `EP01-SEG05` 并写死「仅图1男主碰锤、图2打手禁止拿锤」；可选 `PROP-001-hammer.png` 再重跑

## API 备忘

- fast：`duration_sec` 4–12；薄镜并入邻段，勿硬凑 4s 单独开段
- SEG05a 敏感词已改为「宋家小子，还敢站着？」
